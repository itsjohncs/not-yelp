import argon2
import flask
import flask_sqlalchemy
import werkzeug.exceptions
import sqlalchemy

import re
import secrets


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/toptal-interview-project.db"

db = flask_sqlalchemy.SQLAlchemy(app)

hasher = argon2.PasswordHasher()


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


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
            raise ValidationError(
                f"password must be between {MIN} and {MAX} characters, "
                f"exclusive")

    @sqlalchemy.orm.validates("username")
    def validate_username(self, key, username):
        MIN = 3
        MAX = 30
        if not (MIN < len(username) < MAX):
            raise ValidationError(
                f"username must be between {MIN} and {MAX} characters")

        if not re.match(r"^[0-9A-Za-z_]+$", username):
            raise ValidationError(
                f"username must contain only characters: 0-9, A-Z, a-z, and _")

        return username

    def __repr__(self):
        return "<User %r>" % self.username


@app.errorhandler(ValidationError)
def validation_error(err):
    return {
        "result": "error",
        "message": err.message,
    }


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def otherwise_unhandled_error(err):
    return {
        "result": "error",
        "message": "An unexpected error occurred."
    }


@app.route("/api/register", methods=["POST"])
def register():
    username = flask.request.json.get("username")
    password = flask.request.json.get("password")
    if not username or not password:
        raise ValidationError("username and password are both required fields")

    # Validation of the username and password is done within the model
    account = Account(username=username, password=password)
    db.session.add(account)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise ValidationError("username is already taken")

    return {
        "result": "success",
        "username": username,
        "username": password,
    }


@app.route("/api/login", methods=["POST"])
def login():
    username = flask.request.json.get("username")
    password = flask.request.json.get("password")
    if not username or not password:
        raise ValidationError("username and password are both required fields")

    account = Account.query.filter_by(username=username).first()
    try:
        hasher.verify(account.password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        raise ValidationError("incorrect password")

    return {
        "result": "success",
    }
