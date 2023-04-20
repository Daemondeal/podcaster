from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from flask_bootstrap import Bootstrap5

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

# from flask_session import Session
# Se questo import viene fatto normalmente, mypy non riesce a trovare
# le definizioni per i tipi. Aggiungere .__init__ sembra risolvere il problema
from flask_session.__init__ import Session

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import exceptions

from http import HTTPStatus

from .user_model import User

from .database import db
from .database import dao_users
from .database import dao_series
from .database import dao_episodes
from .database.setup_database import init_db_command

from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse

from . import validation
from . import media

import os
import sqlite3
import datetime

app = Flask(__name__)

# Non si possono inviare file più grandi di 64MB.
app.config["MAX_CONTENT_LENGTH"] = 64 * 1000 * 1000

# Percorso del database
app.config["DATABASE"] = os.path.join(app.instance_path, "database.sqlite")

# I percorsi delle cartelle contenenti le risorse caricate dagli utenti
app.config["USER_IMAGE_PATH"] = os.path.join(app.instance_path, "user_images/")
app.config["SERIES_IMAGE_PATH"] = os.path.join(app.instance_path, "series_images/")
app.config["EPISODE_TRACK_PATH"] = os.path.join(app.instance_path, "episode_tracks/")

# Inizializzazione di bootstrap_flask
Bootstrap5(app)

# Inizializzazione di flask_session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Inizializzazione di flask_login
login_manager = LoginManager()

# flask_login richiede una SECRET_KEY per funzionare
app.config[
    "SECRET_KEY"
] = "551A874E0878E5E90FD4D98228405232DBD3BCFBE14D71ED2C08B6B278A47B82"

# La route a cui si viene reindirizzati se si prova ad accedere
# ad una pagina che richiede autenticazione senza essere autenticati
login_manager.login_view = "route_homepage"

# Il messaggio che viene flashato quando si prova ad accedere
# ad una pagina che richiede autenticazione senza essere autenticati
login_manager.login_message = (
    "Non hai i permessi necessari per visualizzare quella pagina."
)
login_manager.login_message_category = "warning"
login_manager.init_app(app)

# Inizializzazione del database
db.init_app(app)
app.cli.add_command(init_db_command)


@app.route("/")
def route_homepage():
    series = dao_series.get_all_series_with_episode_count()

    return render_template(
        "series_card_view.html", title="Serie Recenti", series_list=series
    )


@app.route("/category/<string:category>")
def route_series_by_category(category):
    series = dao_series.get_series_with_episode_count_from_category(category)

    if len(series) == 0:
        abort(HTTPStatus.NOT_FOUND)

    return render_template("series_card_view.html", series_list=series, title=category)


@app.route("/series/<string:seriesid>")
def route_series(seriesid):
    series = dao_series.get_series_from_id(seriesid)

    if series is None:
        abort(HTTPStatus.NOT_FOUND)

    # Solo i creatori possono vedere episodi programmati per il futuro
    if current_user.is_authenticated and current_user.id == series["Author_UserID"]:
        episodes = dao_episodes.get_episodes_from_series(seriesid)
    else:
        episodes = dao_episodes.get_episodes_from_series_before_date(
            seriesid, datetime.date.today()
        )

    is_current_user_following_series = None
    if current_user.is_authenticated and dao_users.is_user_following_series(
        current_user.id, seriesid
    ):
        is_current_user_following_series = True
    else:
        is_current_user_following_series = False

    return render_template(
        "series/series.html",
        series=series,
        episodes=episodes,
        is_current_user_following_series=is_current_user_following_series,
        accepted_formats=validation.get_supported_image_formats_mime(),
    )


@app.route("/series/create", methods=["GET"])
@login_required
def route_new_series_view():
    if not current_user.is_creator():
        return app.login_manager.unauthorized()

    return render_template(
        "series/create_series.html",
        accepted_formats=validation.get_supported_image_formats_mime(),
    )


@app.route("/series/create", methods=["POST"])
@login_required
def route_new_series():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    image = request.files.get("image")

    if not current_user.is_creator():
        return app.login_manager.unauthorized()

    try:
        validation.validate_series(title, category, description)
        validation.validate_image(image)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(url_for("route_new_series_view"))

    filename = media.save_series_image(image)

    try:
        series_id = dao_series.add_series(
            current_user.id, title, category, description, filename
        )
    except sqlite3.Error as e:
        app.logger.error("Database error: ", e)
        media.remove_series_image(filename)
        flash("Si è verificato un errore inaspettato durante la creazione.", "warning")
        return redirect(url_for("route_new_series_view"))

    return redirect(url_for("route_series", seriesid=series_id))


@app.route("/series/<string:seriesid>/edit", methods=["POST"])
@login_required
def route_edit_series(seriesid: str):
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    image = request.files.get("image")

    series = dao_series.get_series_from_id(seriesid)
    if series is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    try:
        validation.validate_series(title, category, description)

        if image:
            validation.validate_image(image)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(url_for("route_series", seriesid=seriesid))

    try:
        dao_series.update_series_info(seriesid, title, category, description)
    except sqlite3.Error as e:
        app.logger.error("Database error: ", e)
        flash("Si è verificato un errore inaspettato.", "warning")
        return redirect(url_for("route_series", seriesid=seriesid))

    if image:
        old_image_name = series["ImageFilename"]

        filename = media.save_series_image(image)

        try:
            dao_series.update_series_image(seriesid, filename)
        except Exception as e:
            app.logger.error("Unexpected error: ", e)
            media.remove_series_image(filename)
            flash("Si è verificato un errore inaspettato.", "warning")
            return redirect(url_for("route_series", seriesid=seriesid))

        media.remove_series_image(old_image_name)

    return redirect(url_for("route_series", seriesid=seriesid))


@app.route("/series/delete", methods=["POST"])
@login_required
def route_delete_series():
    seriesid = request.form.get("seriesid", "").strip()

    series = dao_series.get_series_from_id(seriesid)
    if series is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    series_image = dao_series.get_series_from_id(seriesid)["ImageFilename"]
    image_path = os.path.join(app.instance_path, "series_images/", series_image)
    os.remove(image_path)
    dao_series.delete_series(seriesid)

    return redirect(url_for("route_homepage"))


@app.route("/series/<string:seriesid>/follow", methods=["POST"])
@login_required
def route_series_follow(seriesid: str):
    series = dao_series.get_series_from_id(seriesid)

    if series is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_users.is_user_following_series(current_user.id, seriesid):
        dao_users.add_user_follow(current_user.id, seriesid)

    return redirect(url_for("route_series", seriesid=seriesid))


@app.route("/series/<string:seriesid>/unfollow", methods=["POST"])
@login_required
def route_series_unfollow(seriesid: str):
    series = dao_series.get_series_from_id(seriesid)

    if series is None:
        abort(HTTPStatus.NOT_FOUND)

    dao_users.delete_user_follow(current_user.id, seriesid)

    return redirect(url_for("route_series", seriesid=seriesid))


@app.route("/series/<string:seriesid>/episode/<string:episodeid>")
def route_episode(seriesid: str, episodeid: str):
    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)
    series = dao_series.get_series_from_id(seriesid)

    if series is None or episode is None:
        abort(HTTPStatus.NOT_FOUND)

    # Solo i creatori possono vedere episodi programmati per il futuro
    if episode["DateInserted"].date() > datetime.date.today() and not (
        current_user.is_authenticated and current_user.id == series["Author_UserID"]
    ):
        abort(HTTPStatus.NOT_FOUND)

    comments = dao_episodes.get_comments_from_episode(seriesid, episodeid)
    is_current_user_following_series = (
        current_user.is_authenticated
        and dao_users.is_user_following_series(current_user.id, seriesid)
    )

    return render_template(
        "episode/episode.html",
        series=series,
        episode=episode,
        comments=comments,
        is_current_user_following_series=is_current_user_following_series,
        accepted_formats=validation.get_supported_audio_formats_mime(),
    )


@app.route("/series/<string:seriesid>/episode/create", methods=["GET"])
@login_required
def route_new_episode_view(seriesid: str):
    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    series = dao_series.get_series_from_id(seriesid)
    current_day = datetime.date.today()

    return render_template(
        "episode/create_episode.html",
        series=series,
        current_day=current_day,
        accepted_formats=validation.get_supported_audio_formats_mime(),
    )


@app.route("/series/<string:seriesid>/episode/create", methods=["POST"])
@login_required
def route_new_episode(seriesid: str):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    date_string = request.form.get("date", "").strip()

    audio_track = request.files.get("track")

    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    try:
        validation.validate_episode(title, description, date_string)
        validation.validate_audio_track(audio_track)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(url_for("route_new_episode_view", seriesid=seriesid))

    assert audio_track is not None

    try:
        filename, track_duration = media.save_episode_track_and_get_length(audio_track)
    except media.UnsupportedFileError:
        flash("Formato audio non supportato.", "warning")
        return redirect(url_for("route_new_episode_view", seriesid=seriesid))

    date = isoparse(date_string)

    try:
        episode_id = dao_episodes.add_episode(
            seriesid, title, description, date, filename, track_duration
        )
    except sqlite3.Error as e:
        app.logger.error("Database error: ", e)

        media.remove_audio_track(filename)
        flash("Si è verificato un errore inaspettato durante la creazione.", "warning")
        return redirect(url_for("route_new_episode_view", seriesid=seriesid))

    return redirect(url_for("route_episode", seriesid=seriesid, episodeid=episode_id))


@app.route(
    "/series/<string:seriesid>/episode/<string:episodeid>/edit", methods=["POST"]
)
@login_required
def route_edit_episode(seriesid: str, episodeid: str):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    date_string = request.form.get("date", "").strip()

    audio_track = request.files.get("track")

    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)
    if episode is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    try:
        validation.validate_episode(title, description, date_string)

        if audio_track:
            validation.validate_audio_track(audio_track)

    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(
            url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
        )

    date = isoparse(date_string)

    try:
        dao_episodes.update_episode_info(seriesid, episodeid, title, description, date)
    except sqlite3.Error as e:
        app.logger.error("Database error: ", e)
        flash("Si è verificato un errore inaspettato.", "warning")
        return redirect(
            url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
        )

    if audio_track:
        old_track_name = episode["TrackFilename"]

        try:
            filename, track_duration = media.save_episode_track_and_get_length(
                audio_track
            )
        except media.UnsupportedFileError:
            flash("Formato audio non supportato.", "warning")
            return redirect(
                url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
            )

        try:
            dao_episodes.update_episode_track(
                seriesid, episodeid, filename, track_duration
            )
        except Exception as e:
            app.logger.error("Unexpected error: ", e)
            assert audio_track.filename is not None
            media.remove_audio_track(audio_track.filename)
            flash(
                "Si è verificato un errore inaspettato durante la modifica.", "warning"
            )
            return redirect(
                url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
            )

        media.remove_audio_track(old_track_name)

    return redirect(url_for("route_episode", seriesid=seriesid, episodeid=episodeid))


@app.route(
    "/series/<string:seriesid>/episode/<string:episodeid>/delete", methods=["POST"]
)
@login_required
def route_delete_episode(seriesid: str, episodeid: str):
    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)

    if episode is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_users.is_user_owner_of_series(current_user.id, seriesid):
        return login_manager.unauthorized()

    track_name = episode["TrackFilename"]

    dao_episodes.delete_episode(seriesid, episodeid)
    media.remove_audio_track(track_name)

    return redirect(url_for("route_series", seriesid=seriesid))


@app.route(
    "/series/<string:seriesid>/episode/<string:episodeid>/comment_new", methods=["POST"]
)
@login_required
def route_new_comment(seriesid: str, episodeid: str):
    comment = request.form.get("comment", "").strip()

    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)

    if episode is None:
        abort(HTTPStatus.NOT_FOUND)

    # Solo i creatori possono vedere episodi programmati per il futuro
    if episode["DateInserted"].date() > datetime.date.today() and not (
        current_user.is_authenticated
        and dao_users.is_user_owner_of_series(
            current_user.id, episode["Series_PodcastSeriesID"]
        )
    ):
        abort(HTTPStatus.NOT_FOUND)

    try:
        validation.validate_comment(comment)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(
            url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
        )

    now = datetime.datetime.now()

    dao_episodes.add_comment(current_user.id, seriesid, episodeid, comment, now)

    return redirect(url_for("route_episode", seriesid=seriesid, episodeid=episodeid))


@app.route(
    "/series/<string:seriesid>/episode/<string:episodeid>/comment_delete",
    methods=["POST"],
)
@login_required
def route_delete_comment(seriesid: str, episodeid: str):
    commentid = request.form.get("commentid")

    if commentid is None:
        abort(HTTPStatus.BAD_REQUEST)

    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)

    if episode is None:
        abort(HTTPStatus.NOT_FOUND)

    if not dao_episodes.is_comment_owned_by_user(current_user.id, commentid):
        flash("Non puoi cancellare commenti che non sono i tuoi", "warning")
    else:
        dao_episodes.delete_comment(commentid)

    return redirect(url_for("route_episode", seriesid=seriesid, episodeid=episodeid))


@app.route(
    "/series/<string:seriesid>/episode/<string:episodeid>/comment_edit",
    methods=["POST"],
)
@login_required
def route_edit_comment(seriesid: str, episodeid: str):
    commentid = request.form.get("commentid")
    comment = request.form.get("comment", "").strip()

    if commentid is None:
        abort(HTTPStatus.BAD_REQUEST)

    episode = dao_episodes.get_episode_from_id(seriesid, episodeid)

    if episode is None:
        abort(HTTPStatus.NOT_FOUND)

    try:
        validation.validate_comment(comment)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(
            url_for("route_episode", seriesid=seriesid, episodeid=episodeid)
        )

    if not dao_episodes.is_comment_owned_by_user(current_user.id, commentid):
        flash("Non puoi modificare commenti che non sono i tuoi", "warning")
    else:
        dao_episodes.update_comment(commentid, comment)

    return redirect(url_for("route_episode", seriesid=seriesid, episodeid=episodeid))


@app.route("/user/<string:userid>")
def route_user(userid: str):
    user = dao_users.get_user_from_id(userid)

    if user is None:
        abort(HTTPStatus.NOT_FOUND)

    series_created = dao_users.get_series_from_user(userid)
    series_followed = dao_users.get_follows_from_user(userid)

    for series in series_followed:
        app.logger.info(series["Title"])

    return render_template(
        "user/user.html",
        user=user,
        series_created=series_created,
        series_followed=series_followed,
    )


@app.route("/signup", methods=["GET"])
def route_signup_view():
    if current_user.is_authenticated:
        return redirect(url_for("route_homepage"))

    return render_template(
        "user/signup.html",
        accepted_formats=validation.get_supported_image_formats_mime(),
    )


@app.route("/signup", methods=["POST"])
def route_signup():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password_cleartext = request.form.get("password", "").strip()
    user_type = request.form.get("usertype", "").strip()

    image = request.files.get("image")

    if current_user.is_authenticated:
        flash("Sei già registrato", "warning")
        return redirect(url_for("route_signup_view"))

    try:
        validation.validate_user(name, email, user_type, password_cleartext)
        validation.validate_image(image)
    except validation.ValidationError as error:
        flash(error.message, "warning")
        return redirect(url_for("route_signup_view"))

    hashed_password = generate_password_hash(password_cleartext)

    filename = media.save_user_image(image)

    try:
        if user_type == "Creator":
            new_user_id = dao_users.add_creator(name, filename, email, hashed_password)
        elif user_type == "Listener":
            new_user_id = dao_users.add_listener(name, filename, email, hashed_password)
    except sqlite3.Error as e:
        app.logger.error("Database error: ", e)
        flash(
            "Si è verificato un errore inaspettato durante la registrazione.", "warning"
        )

        # Se non è stato possibile aggiungere l'utente nel database,
        # rimuovi l'immagine utente dalla cartella
        media.remove_user_image(filename)

        return redirect(url_for("route_signup_view"))

    # Esegue il login immediatamente dopo aver creato l'utente
    login_user(load_user(new_user_id))
    return redirect(url_for("route_homepage"))


@app.route("/login", methods=["POST"])
def route_login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    remember_me = request.form.get("remember-me") is not None
    redirect_url = request.form.get("redirect-back")

    user = dao_users.get_user_and_password_from_email(email)

    if user is not None and check_password_hash(user["Password"], password):
        user_model = User(
            id=user["UserID"],
            user_type=user["UserType"],
            name=user["Name"],
            email=user["Email"],
            image_filename=user["ProfileImageFilename"],
        )

        login_user(user_model, remember=remember_me)
    else:
        flash("Nome utente o password errati", "danger")

    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect(url_for("route_homepage"))


@app.route("/logout", methods=["POST"])
@login_required
def route_logout():
    redirect_url = request.form.get("redirect-back")

    logout_user()

    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect(url_for("route_homepage"))


@app.route("/track/<string:filename>")
@login_required
def route_track(filename: str):
    return send_from_directory(app.config["EPISODE_TRACK_PATH"], filename)


@app.route("/user_images/<string:filename>")
def route_user_image(filename: str):
    return send_from_directory(app.config["USER_IMAGE_PATH"], filename)


@app.route("/series_images/<string:filename>")
def route_series_image(filename: str):
    return send_from_directory(app.config["SERIES_IMAGE_PATH"], filename)


@login_manager.user_loader
def load_user(user_id: str) -> User:
    user = dao_users.get_user_from_id(user_id)
    return User(
        id=user["UserID"],
        user_type=user["UserType"],
        name=user["Name"],
        email=user["Email"],
        image_filename=user["ProfileImageFilename"],
    )


# Le pagine che vengono mostrate quando
# il server ritorna un errore specifico.
# https://flask.palletsprojects.com/en/2.2.x/errorhandling/#error-handlers
@app.errorhandler(exceptions.NotFound)
def route_error_not_found(e):
    return (
        render_template(
            "error.html",
            error_title="404 Not Found",
            error_code="404",
            error_description="Pagina non trovata",
        ),
        HTTPStatus.NOT_FOUND,
    )


@app.errorhandler(exceptions.Unauthorized)
def route_error_unauthorized(e):
    return (
        render_template(
            "error.html",
            error_title="401 Unauthorized",
            error_code="401",
            error_description="Utente non autorizzato",
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@app.errorhandler(exceptions.BadRequest)
def route_error_bad_request(e):
    return (
        render_template(
            "error.html",
            error_title="400 Bad Request",
            error_code="400",
            error_description="Richiesta Invalida",
        ),
        HTTPStatus.BAD_REQUEST,
    )


@app.errorhandler(exceptions.InternalServerError)
def route_error_internal_server(e):
    return (
        render_template(
            "error.html",
            error_title="500 Internal Server Error",
            error_code="500",
            error_description="Errore Interno",
        ),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


# Visto che ci sono alcune variabili richieste da ogni template,
# questo metodo le inietta in ogni template automaticamente
# https://flask.palletsprojects.com/en/2.2.x/templating/#context-processors
@app.context_processor
def inject_values_into_all_templates():
    default_values = {}

    default_values["categories"] = dao_series.get_all_categories()

    if current_user.is_authenticated:
        default_values["followed_series"] = dao_users.get_follows_from_user(
            current_user.id
        )

    return default_values


# Filtri custom per jinja2
# https://flask.palletsprojects.com/en/2.2.x/templating/#registering-filters
@app.template_filter("format_duration")
def format_time_filter(time_seconds: int) -> str:
    minutes, seconds = divmod(time_seconds, 60)
    return f"{minutes:02}:{seconds:02}"


@app.template_filter("format_past_date")
def format_past_date_filter(date_with_time: datetime.datetime) -> str:
    date = date_with_time.date()
    now = datetime.date.today()

    if date > now:
        delta = relativedelta(date, now)
        is_future = True
    else:
        delta = relativedelta(now, date)
        is_future = False

    for name, singular, plural in [
        ("years", "anno", "anni"),
        ("months", "mese", "mesi"),
        ("days", "giorno", "giorni"),
    ]:
        amount = getattr(delta, name)
        if is_future:
            if amount == 1:
                return f"tra 1 {singular}"
            elif amount > 1:
                return f"tra {amount} {plural}"
        else:
            if amount == 1:
                return f"1 {singular} fa"
            elif amount > 1:
                return f"{amount} {plural} fa"

    return "oggi"


@app.template_filter("format_past_datetime")
def format_past_datetime_filter(date: datetime.datetime) -> str:
    now = datetime.datetime.now()

    if date > now:
        delta = relativedelta(date, now)
        is_future = True
    else:
        delta = relativedelta(now, date)
        is_future = False

    for name, singular, plural in [
        ("years", "anno", "anni"),
        ("months", "mese", "mesi"),
        ("days", "giorno", "giorni"),
        ("hours", "ora", "ore"),
        ("minutes", "minuto", "minuti"),
    ]:
        amount = getattr(delta, name)
        if is_future:
            if amount == 1:
                return f"tra 1 {singular}"
            elif amount > 1:
                return f"tra {amount} {plural}"
        else:
            if amount == 1:
                return f"1 {singular} fa"
            elif amount > 1:
                return f"{amount} {plural} fa"

    if is_future:
        return "tra qualche secondo"
    return "qualche secondo fa"
