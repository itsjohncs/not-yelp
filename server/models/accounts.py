import sqlalchemy

from app import db
import custom_errors


class Account(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    username = db.Column(db.Text(collation="NOCASE"), unique=True, nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)

    def __init__(self, *, password=None, id=None, **kwargs):
        if password is not None:
            if "password_hash" in kwargs:
                raise ArgumentError(
                    "password and password_hash cannot both be given")

            kwargs["password_hash"] = hasher.hash(password)

        kwargs["id"] = self.generate_id() if id is None else id

        super().__init__(**kwargs)

    @staticmethod
    def generate_id():
        return secrets.token_hex(8)

    def validate_password(self, password):
        MIN = 5
        MAX = 100
        if not (MIN < len(password) < MAX):
            raise custom_errors.ValidationError(
                f"password must be between {MIN} and {MAX} characters, "
                f"exclusive")

    @sqlalchemy.orm.validates("username")
    def validate_username(self, key, username):
        MIN = 3
        MAX = 30
        if not (MIN < len(username) < MAX):
            raise custom_errors.ValidationError(
                f"username must be between {MIN} and {MAX} characters")

        if not re.match(r"^[0-9A-Za-z_]+$", username):
            raise custom_errors.ValidationError(
                f"username must contain only characters: 0-9, A-Z, a-z, and _")

        return username

    def __repr__(self):
        return "<User %r>" % self.username
