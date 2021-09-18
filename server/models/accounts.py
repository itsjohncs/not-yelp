from enum import Enum, auto
import re

import sqlalchemy
import argon2

from app import db
import custom_errors
from models.model_ids import generate_id
from models.decorators import not_none


password_hasher = argon2.PasswordHasher()


class Permission(Enum):
    # Gives each enum the value of its name. For example:
    # CREATE_ADMIN_USER.value == "CREATE_ADMIN_USER"
    # pylint: disable-next=E0213
    def _generate_next_value_(name, _start, _count, _last_values):
        return name

    CREATE_ADMIN_ACCOUNT = auto()
    CREATE_RESTAURANT = auto()
    CREATE_REVIEW = auto()
    CREATE_REVIEW_REPLY = auto()


def has_permission(account, permission):
    if not account:
        return False

    roles = account.roles
    return (
        "admin" in account.roles or
        (permission is Permission.CREATE_RESTAURANT and "owner" in roles) or
        (permission is Permission.CREATE_REVIEW and "patron" in roles) or
        (permission is Permission.CREATE_REVIEW_REPLY and "owner" in roles))


class Account(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    username = db.Column(db.Text(collation="NOCASE"), unique=True,
                         nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)
    roles = db.Column(db.JSON(), nullable=False)

    KNOWN_ROLES = {"admin", "owner", "patron"}

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
        if not MIN <= len(username) <= MAX:
            raise custom_errors.ValidationError(
                f"username must be between {MIN} and {MAX} characters "
                f"inclusive")

        if not re.match(r"^[0-9A-Za-z_]+$", username):
            raise custom_errors.ValidationError(
                "username must contain only characters: 0-9, A-Z, a-z, and _")

        return username

    @sqlalchemy.orm.validates("roles")
    @not_none
    def validate_roles(self, _key, roles):
        if not isinstance(roles, list):
            raise custom_errors.ValidationError("roles must be a list")
        elif any(i not in self.KNOWN_ROLES for i in roles):
            raise custom_errors.ValidationError(
                f"each role must be one of {self.KNOWN_ROLES}")
        elif len(set(roles)) != len(roles):
            raise custom_errors.ValidationError("each role must be unique")

        return roles
