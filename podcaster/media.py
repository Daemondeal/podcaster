from PIL import Image

import os
import uuid
import mutagen

from werkzeug.datastructures import FileStorage
from flask import current_app


class UnsupportedFileError(Exception):
    pass


def remove_user_image(image_name: str):
    image_path = os.path.join(current_app.config["USER_IMAGE_PATH"], image_name)
    os.remove(image_path)


def remove_series_image(image_name: str):
    image_path = os.path.join(current_app.config["SERIES_IMAGE_PATH"], image_name)
    os.remove(image_path)


def remove_audio_track(track_name: str):
    image_path = os.path.join(current_app.config["EPISODE_TRACK_PATH"], track_name)
    os.remove(image_path)


def save_user_image(image: FileStorage) -> str:
    assert image.filename is not None

    guid_filename = randomize_filename(image.filename)
    image_path = os.path.join(current_app.config["USER_IMAGE_PATH"], guid_filename)

    resized_image = get_resized_image(image, 192, 192)
    resized_image.save(image_path)

    return guid_filename


def save_series_image(image: FileStorage) -> str:
    assert image.filename is not None

    guid_filename = randomize_filename(image.filename)
    image_path = os.path.join(current_app.config["SERIES_IMAGE_PATH"], guid_filename)

    resized_image = get_resized_image(image, 512, 512)
    resized_image.save(image_path)

    return guid_filename


def save_episode_track_and_get_length(track: FileStorage) -> tuple[str, float]:
    assert track.filename is not None

    guid_filename = randomize_filename(track.filename)
    track_path = os.path.join(current_app.config["EPISODE_TRACK_PATH"], guid_filename)

    track.save(track_path)

    # È necessario leggere il file di nuovo perché creare un mutagen
    # file handle consuma il file, e rende impossibile salvarlo di nuovo
    # senza passare per i metodi di mutagen. Per evitare di dover usare il
    # metodo save di mutagen (Che non è documentato bene), si salva prima il file
    # e poi lo si legge.
    handle = mutagen.File(track_path)

    if not handle:
        os.remove(track_path)
        raise UnsupportedFileError()

    duration = handle.info.length

    return guid_filename, duration


def get_resized_image(image: FileStorage, width: int, height: int) -> Image:
    pil_image = Image.open(image)

    return pil_image.resize(size=(width, height))


def randomize_filename(filename: str) -> str:
    _, extension = os.path.splitext(filename)

    name = str(uuid.uuid4())

    return f"{name}{extension}"
