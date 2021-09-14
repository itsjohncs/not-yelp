import flask
import flask_sqlalchemy


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/toptal-interview-project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# genereate new key with `secrets.token_bytes(20)`
app.secret_key = b'\x1dz\xf2\xbd\x91\xff\xf1\xb8\xfc\xef\x85z\xad\x98\x8c\x95^\x9f\xc0\x9b'

db = flask_sqlalchemy.SQLAlchemy(app)

class CustomEncoder(flask.json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, db.Model):
			return obj.to_serializable()

		return super().default(obj)
app.json_encoder = CustomEncoder

import models  # pylint: disable=C0413,W0611
import handlers  # pylint: disable=C0413,W0611
