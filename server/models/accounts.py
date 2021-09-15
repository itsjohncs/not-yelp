import re

import sqlalchemy
import argon2

from app import db
import custom_errors
from models.model_ids import generate_id
from models.decorators import not_none


password_hasher = argon2.PasswordHasher()


class Account(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    username = db.Column(db.Text(collation="NOCASE"), unique=True, nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)

    def __init__(self, *, password=None, id=None, **kwargs):
        if password is not None:
            if "password_hash" in kwargs:
                raise ValueError(
                    "password and password_hash cannot both be given")

            self.validate_password(password)
            kwargs["password_hash"] = password_hasher.hash(password)

        kwargs["id"] = generate_id() if id is None else id

        super().__init__(**kwargs)

    @staticmethod
    def validate_password(password):
        MIN = 5
        MAX = 100
        if not MIN < len(password) < MAX:
            raise custom_errors.ValidationError(
                f"password must be between {MIN} and {MAX} characters, "
                f"exclusive")

    @sqlalchemy.orm.validates("username")
    @not_none
    def validate_username(self, _key, username):
        MIN = 3
        MAX = 30
        if not MIN < len(username) < MAX:
            raise custom_errors.ValidationError(
                f"username must be between {MIN} and {MAX} characters")

        if not re.match(r"^[0-9A-Za-z_]+$", username):
            raise custom_errors.ValidationError(
                "username must contain only characters: 0-9, A-Z, a-z, and _")

        return username

    def __repr__(self):
        return f"<Account {self.id}>"
