from podcaster.database import dao_users

from werkzeug.datastructures import FileStorage

import re


class ValidationError(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
        return super().__init__(self, message)


ACCEPTED_IMAGE_FORMATS = [
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
]

ACCEPTED_AUDIO_FORMATS = [
    "audio/wav",
    "audio/ogg",
    "audio/mpeg",
    "video/ogg",  # Firefox invia i file audio ogg con mimetype video/ogg
]


def get_supported_image_formats_mime() -> str:
    return ",".join(ACCEPTED_IMAGE_FORMATS)


def get_supported_audio_formats_mime() -> str:
    return ",".join(ACCEPTED_AUDIO_FORMATS)


def validate_image(image: FileStorage | None):
    if image is None or image.filename is None:
        raise ValidationError("Inserire un'Immagine.")

    if image.mimetype not in ACCEPTED_IMAGE_FORMATS:
        raise ValidationError("Il formato dell'immagine non è supportato.")


def validate_audio_track(audio_track: FileStorage | None):
    if audio_track is None or audio_track.filename == "":
        raise ValidationError("Inserire una Traccia Audio.")

    if audio_track.mimetype is None:
        raise ValidationError("Il formato audio non è supportato.")


def validate_user(name: str, email: str, user_type: str, password: str):
    if len(name) < 1:
        raise ValidationError("Inserire un Nome Utente.")

    if len(email) < 1 or len(email) > 255 or "@" not in email:
        raise ValidationError("Inserire una Email Valida")

    if len(password) < 1:
        raise ValidationError("Inserire una Password.")

    if len(password) < 6:
        raise ValidationError("Password troppo corta, usare almeno 6 caratteri.")

    if len(name) > 50:
        raise ValidationError("Il Nome Utente non può superare i 50 caratteri.")

    if len(password) > 255:
        raise ValidationError("La Password non può superare i 255 caratteri.")

    if user_type not in ["Creator", "Listener"]:
        raise ValidationError("Il Tipo Utente è invalido.")

    if dao_users.is_email_taken(email):
        raise ValidationError("Questa email è già in uso.")


def validate_series(title: str, category: str, description: str):
    if len(title) < 1:
        raise ValidationError("Inserire un Titolo.")

    if len(category) < 1:
        raise ValidationError("Inserire una Categoria.")

    if len(description) < 1:
        raise ValidationError("Inserire una Descrizione.")

    if len(title) > 100:
        raise ValidationError("Il Titolo non può superare i 100 caratteri.")

    if len(category) > 50:
        raise ValidationError("La Categoria non può superare i 50 caratteri.")

    if len(description) > 1000:
        raise ValidationError("La Descrizione non può superare i 1000 caratteri.")


def validate_episode(title: str, description: str, date: str):
    if len(title) < 1:
        raise ValidationError("Inserire un Titolo.")

    if len(description) < 1:
        raise ValidationError("Inserire una Descrizione.")

    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
        raise ValidationError("Inserire una Data valida.")

    if len(title) >= 100:
        raise ValidationError("Il Titolo non può superare i 100 caratteri.")

    if len(description) >= 1000:
        raise ValidationError("La Descrizione non può superare i 1000 caratteri.")


def validate_comment(content: str):
    if len(content) < 1:
        raise ValidationError("Il Commento non può essere vuoto.")

    if len(content) > 1000:
        raise ValidationError("Il Commento non può superare i 1000 caratteri.")
