from flask_login import UserMixin


class User(UserMixin):
    id: str
    user_type: str
    name: str
    email: str
    image_filename: str

    def __init__(
        self, id: str, user_type: str, name: str, email: str, image_filename: str
    ):
        self.id = id
        self.user_type = user_type
        self.name = name
        self.email = email
        self.image_filename = image_filename

    def is_creator(self) -> bool:
        return self.user_type == "Creator"

    def is_listener(self) -> bool:
        return self.user_type == "Listener"
