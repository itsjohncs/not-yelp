import sqlalchemy

from app import db
import custom_errors
from models.model_ids import generate_id
from models.decorators import not_none
from models.accounts import Account


class Restaurant(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    owner = db.Column(db.String(16), db.ForeignKey(Account.id),
                      nullable=False)
    average_rating = db.Column(db.Float())

    def __init__(self, *, id=None, **kwargs):
        kwargs["id"] = generate_id() if id is None else id
        super().__init__(**kwargs)

    @sqlalchemy.orm.validates("title")
    @not_none
    def validate_title(self, _key, title):
        if len(title) <= 1:
            raise custom_errors.ValidationError(
                "title must be more than 1 character")
        return title

    def to_serializable(self):
        return {
            "id": self.id,
            "title": self.title,
            "owner": self.owner,
            "average_rating": self.average_rating,
        }
