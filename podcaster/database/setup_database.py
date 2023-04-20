import datetime
import io
import random
import dateutil
from flask import current_app
from werkzeug.security import generate_password_hash
from podcaster import validation
from podcaster import media

from werkzeug.datastructures import FileStorage

from . import db
from . import dao_episodes
from . import dao_series
from . import dao_users

import os
import click
import shutil


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database initialized")


def init_db():
    try:
        shutil.rmtree(current_app.instance_path)
    except:
        pass
    os.makedirs(current_app.instance_path)

    if os.path.exists(current_app.config["DATABASE"]):
        os.remove(current_app.config["DATABASE"])

    connection = db.get_connection()

    with open("./database/create_db.sql") as script_file:
        connection.executescript(script_file.read())

    os.makedirs(current_app.config["USER_IMAGE_PATH"])
    os.makedirs(current_app.config["SERIES_IMAGE_PATH"])
    os.makedirs(current_app.config["EPISODE_TRACK_PATH"])

    populate_database()


def add_user(name, image, email, password, type) -> str:
    setup_path = "./setup/"

    validation.validate_user(name, email, type, password)

    hashed_password = generate_password_hash(password)
    with open(os.path.join(setup_path, image), "rb") as image_file:
        image_storage = FileStorage(image_file, filename=image)
        image_name = media.save_user_image(image_storage)  # type: ignore

    if type == "Creator":
        return dao_users.add_creator(name, image_name, email, hashed_password)
    else:
        return dao_users.add_listener(name, image_name, email, hashed_password)


def add_series(title, description, image, category, author_id) -> str:
    setup_path = "./setup/"

    validation.validate_series(title, category, description)

    with open(os.path.join(setup_path, image), "rb") as image_file:
        image_storage = FileStorage(image_file, filename=image)
        image_name = media.save_series_image(image_storage)  # type: ignore

    return dao_series.add_series(
        author_id, title, category, description.strip(), image_name
    )


def add_episode(title, description, track, date, series_id):
    setup_path = "./setup/"

    validation.validate_episode(title, description, date)

    path = os.path.join(setup_path, track)

    with open(path, "rb") as track_file:
        track_storage = FileStorage(track_file)

        track_name, track_duration = media.save_episode_track_and_get_length(
            track_storage
        )

    return dao_episodes.add_episode(
        series_id,
        title,
        description.strip(),
        dateutil.parser.isoparse(date),
        track_name,
        track_duration,
    )


def get_random_track():
    return random.choice(
        [
            "track1.mp3",
            "track2.mp3",
            "track3.mp3",
            "track4.mp3",
        ]
    )


def populate_database():
    today = datetime.datetime.today().isoformat()
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat()
    last_week = (datetime.datetime.today() - datetime.timedelta(days=7)).isoformat()
    in_one_week = (datetime.datetime.today() + datetime.timedelta(days=7)).isoformat()

    marco_rossi = add_user(
        "Marco Rossi",
        "marcorossi.jpg",
        "marco.rossi@example.org",
        "password",
        "Creator",
    )

    giovanni_lombardi = add_user(
        "Giovanni Lombardi",
        "giovannilombardi.jpg",
        "giovanni.lombardi@example.org",
        "password",
        "Creator",
    )

    maria_giordano = add_user(
        "Maria Giordano",
        "mariagiordano.jpg",
        "maria.giordano@example.org",
        "password",
        "Creator",
    )

    giulia_bianchi = add_user(
        "Giulia Bianchi",
        "giuliabianchi.jpg",
        "giulia.bianchi@example.org",
        "password",
        "Listener",
    )

    andrea_neri = add_user(
        "Andrea Neri",
        "andreaneri.jpg",
        "andrea.neri@example.org",
        "password",
        "Listener",
    )

    roberto_verde = add_user(
        "Roberto Verde",
        "robertoverde.jpg",
        "roberto.verde@example.org",
        "password",
        "Listener",
    )

    history1 = add_series(
        "La Storia Nascosta",
        """
        "La Storia Nascosta" è un podcast dove si esplorano gli aspetti meno conosciuti della storia. Il conduttore, un esperto di storia, si immergerà in eventi e personaggi poco conosciuti ma di grande importanza per comprendere meglio il passato e il presente. Ogni episodio esaminerà un evento o un personaggio specifico, svelando nuove prospettive e rivelando dettagli inediti. Attraverso una narrazione coinvolgente e una ricerca meticolosa, gli ascoltatori scopriranno segreti della storia che sono stati nascosti per troppo tempo e che possono cambiare il modo in cui vediamo il mondo. Una vera e propria esplorazione della storia per gli appassionati e per chi vuole saperne di più.
        """,
        "history1.jpg",
        "Storia e Cultura",
        marco_rossi,
    )

    history1ep1 = add_episode(
        "L'omicidio di Rasputin: il mistero dietro una delle morti più controverse della storia",
        """
        Rasputin è stato uno dei personaggi più misteriosi e controversi della storia russa. Nel questo episodio esploreremo le circostanze della sua morte, avvenuta nel 1916. Attraverso testimonianze e documenti d'archivio, scopriremo le diverse versioni dei fatti e cercheremo di fare chiarezza su uno dei delitti più misteriosi della storia. Cosa c'è dietro l'omicidio di Rasputin? Chi era davvero l'uomo che ha avuto un'enorme influenza sulla famiglia imperiale russa?
        """,
        get_random_track(),
        last_week,
        history1,
    )

    history1ep2 = add_episode(
        "La vera storia della principessa Anastasia",
        """
        La Principessa Anastasia è diventata una leggenda dopo la morte della famiglia imperiale russa. Nel questo episodio esploreremo la vera storia di Anastasia, al di là della leggenda e delle numerose pretese di essere sopravvissuta al massacro. Attraverso documenti d'archivio e testimonianze, scopriremo la verità sulla sua vita e la sua morte, e ci chiederemo se davvero Anastasia sia sopravvissuta alla strage della sua famiglia.
        """,
        get_random_track(),
        yesterday,
        history1,
    )

    history1ep3 = add_episode(
        "Il complotto della Mano Nera: Una delle più grandi truffe della storia",
        """
        La Mano Nera è stata una delle più grandi truffe della storia. Nel questo episodio esploreremo la vera storia dietro questo complotto, che ha sconvolto l'Europa alla fine del XIX secolo. Attraverso documenti d'archivio e testimonianze, scopriremo come un gruppo di criminali è riuscito a ingannare la polizia e l'opinione pubblica, seminando il panico e il terrore. Cosa c'è dietro la Mano Nera e come è riuscita a ingannare così tante persone per così tanto tempo?
        """,
        get_random_track(),
        in_one_week,
        history1,
    )

    history2 = add_series(
        "Segreti delle Grandi Città",
        """
        "Segreti delle Grandi Città" è un podcast dove si esplorano gli aspetti meno conosciuti delle grandi città del mondo. Il conduttore, Marco Rossi, un esperto di storia e cultura urbana, si immergerà in eventi e personaggi poco conosciuti ma di grande importanza per comprendere meglio il passato e il presente di alcune delle più famose città del mondo. Ogni episodio esaminerà un evento o un personaggio specifico, svelando nuove prospettive e rivelando dettagli inediti. Attraverso una narrazione coinvolgente e una ricerca meticolosa, gli ascoltatori scopriranno segreti delle grandi città che sono stati nascosti per troppo tempo e che possono cambiare il modo in cui vediamo queste metropoli. Una vera e propria esplorazione della storia urbana per gli appassionati e per chi vuole saperne di più.
        """,
        "history2.jpg",
        "Storia e Cultura",
        marco_rossi,
    )

    history2ep1 = add_episode(
        "Il mistero delle Piramidi di Giza: verità e leggende",
        """
        Le Piramidi di Giza sono uno dei siti archeologici più famosi e misteriosi del mondo. In questo episodio esploreremo le teorie e le leggende che circondano queste antiche costruzioni, cercando di fare chiarezza su come sono state costruite e per quale scopo. Attraverso testimonianze e analisi scientifiche, scopriremo i segreti delle Piramidi di Giza e ci chiederemo se ci sono ancora misteri da svelare.
        """,
        get_random_track(),
        last_week,
        history2,
    )

    history2ep2 = add_episode(
        "Il segreto delle catacombe di Parigi: un viaggio nell'aldilà",
        """
        Le catacombe di Parigi sono uno dei luoghi più misteriosi e affascinanti della città. In questo episodio esploreremo la storia e le leggende delle catacombe, un labirinto di tunnel sotterranei dove sono stati sepolti milioni di parigini. Attraverso testimonianze e documenti d'archivio, scopriremo i segreti delle catacombe di Parigi e ci chiederemo se ci sono ancora misteri da svelare.
        """,
        get_random_track(),
        today,
        history2,
    )

    science = add_series(
        "Esplorando le Scienze Naturali",
        """
        "Esplorando le Scienze Naturali" è un podcast dove si esplorano gli aspetti meno conosciuti delle scienze naturali, come la biologia, la chimica, la fisica e l'astronomia. Il conduttore, la Dr. Maria Giordano, una esperta di scienze naturali, si immergerà in eventi e scoperte poco conosciuti ma di grande importanza per comprendere meglio il nostro mondo e l'universo. Ogni episodio esaminerà un evento o una scoperta specifico, svelando nuove prospettive e rivelando dettagli inediti. Attraverso una narrazione coinvolgente e una ricerca meticolosa, gli ascoltatori scopriranno i segreti delle scienze naturali che sono stati nascosti per troppo tempo e che possono cambiare il modo in cui vediamo il mondo. Una vera e propria esplorazione delle scienze naturali per gli appassionati e per chi vuole saperne di più.
        """,
        "science.jpg",
        "Scienza e Tecnologia",
        maria_giordano,
    )

    economy = add_series(
        "Dietro le quinte del business",
        "Impara i segreti del successo dai leader del settore e scopri come pensano e agiscono.",
        "economy.jpg",
        "Economia e Business",
        giovanni_lombardi,
    )

    economy1ep1 = add_episode(
        "Il segreto del successo di XYZ CEO: cosa lo ha reso così di successo?",
        """
        In questo episodio, parleremo con il CEO di XYZ per scoprire i suoi segreti del successo e come è riuscito a creare una delle più grandi aziende del mondo. Discuteremo anche le sfide che ha dovuto affrontare e come ha superato gli ostacoli per raggiungere il successo.
        """,
        get_random_track(),
        last_week,
        economy,
    )

    economy1ep2 = add_episode(
        "Il futuro del business: cosa aspettarsi dall'economia mondiale",
        """
        In questo episodio, parleremo con economisti e analisti per capire cosa ci aspetta nel futuro del business e come l'economia mondiale sta cambiando. Discuteremo anche le opportunità e le sfide che le aziende dovranno affrontare in futuro e come possono prepararsi per questi cambiamenti.        
        """,
        get_random_track(),
        yesterday,
        economy,
    )

    economy1ep3 = add_episode(
        "Il dietro le quinte della fusione XYZ-ABC: I retroscena di un'operazione miliardaria",
        """
        In questo episodio, parleremo con i dirigenti di XYZ e ABC per scoprire i retroscena della loro fusione da miliardi di dollari. Discuteremo anche le sfide che hanno dovuto aff
        """,
        get_random_track(),
        today,
        economy,
    )

    cultura = add_series(
        "Scoprendo la Cultura Africana: Viaggio nel Sahel",
        """
        "Scoprendo la Cultura Africana: Viaggio nel Sahel" è una serie di podcast che esplora l'affascinante cultura del Sahel, una regione che si estende attraverso il Nord Africa. Attraverso interviste con esperti, musicisti e artisti locali, questa serie ti porterà in un viaggio attraverso la storia, la tradizione e la vita quotidiana dei popoli del Sahel. Impara sulla loro arte, cucina, musica, religione e molto altro ancora. Questa serie è perfetta per chi è interessato ad approfondire la conoscenza dell'Africa e per coloro che vogliono scoprire una cultura unica e affascinante. 
        """,
        "sahel.jpg",
        "Viaggi ed Esplorazioni",
        marco_rossi,
    )

    series_list = [history1, history2, science, economy]

    users = [
        marco_rossi,
        giovanni_lombardi,
        maria_giordano,
        giulia_bianchi,
        andrea_neri,
        roberto_verde,
    ]

    for user in users:
        for series in random.sample(series_list, k=random.randint(0, 3)):
            dao_users.add_user_follow(user, series)

    dao_episodes.add_comment(
        marco_rossi,
        history1,
        history1ep1,
        "Primo!",
        dateutil.parser.isoparse(last_week),
    )
    dao_episodes.add_comment(
        andrea_neri,
        history1,
        history1ep1,
        "Bell'episodio!",
        dateutil.parser.isoparse(last_week),
    )
    dao_episodes.add_comment(
        roberto_verde, history2, history2ep1, "Prova!", dateutil.parser.isoparse(today)
    )
    dao_episodes.add_comment(
        maria_giordano,
        economy,
        economy1ep3,
        "Questo è un commento!",
        dateutil.parser.isoparse(yesterday),
    )

    dao_episodes.add_comment(
        maria_giordano,
        economy,
        economy1ep2,
        "Salvia!",
        dateutil.parser.isoparse(yesterday),
    )

    dao_episodes.add_comment(
        roberto_verde,
        economy,
        economy1ep2,
        "Ciao Maria!",
        dateutil.parser.isoparse(today),
    )
