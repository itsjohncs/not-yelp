import flask
from flask_sqlalchemy import SQLAlchemy
import argon2

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/toptal-interview-project.db"

db = SQLAlchemy(app)

hasher = argon2.PasswordHasher()


class Account(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


@app.route("/api/hello")
def hello_world():
    return {
        "msg": "hello world",
    }
