import flask
import argon2

from app import app
from models.accounts import Account


hasher = argon2.PasswordHasher()


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

    flask.session["logged_in_account_id"] = account.id

    return {
        "result": "success",
    }


@app.route("/api/whoami", methods=["GET"])
def whoami():
    account_id = flask.session.get("logged_in_account_id")
    if account_id:
        account = Account.query.filter_by(id=account_id).first()
        if account:
            return {
                "result": "success",
                "id": account.id,
                "username": account.username,
            }

    return {
        "result": "success",
        "id": None,
        "username": None,
    }
