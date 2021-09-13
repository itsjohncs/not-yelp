import secrets
import re

import sqlalchemy
import argon2

from app import db
import custom_errors


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

            kwargs["password_hash"] = password_hasher.hash(password)

        kwargs["id"] = self.generate_id() if id is None else id

        super().__init__(**kwargs)

    @staticmethod
    def generate_id():
        return secrets.token_hex(8)

    @staticmethod
    def validate_password(password):
        MIN = 5
        MAX = 100
        if not MIN < len(password) < MAX:
            raise custom_errors.ValidationError(
                f"password must be between {MIN} and {MAX} characters, "
                f"exclusive")

    @staticmethod
    @sqlalchemy.orm.validates("username")
    def validate_username(_key, username):
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
        return "<User %r>" % self.username
