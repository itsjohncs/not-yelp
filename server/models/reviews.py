import datetime

import sqlalchemy

from app import db
import custom_errors
from models.model_ids import generate_id
from models.decorators import not_none


class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.String(16), primary_key=True)
    visit_date = db.Column(db.Date(), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    author = db.Column(db.ForeignKey("account.id"), nullable=False)

    def __init__(self, *, id=None, **kwargs):
        kwargs["id"] = generate_id() if id is None else id
        super().__init__(**kwargs)

    @sqlalchemy.orm.validates("visit_date")
    @not_none
    def validate_visit_date(self, _key, visit_date):
        two_days_from_now = datetime.date.today() + datetime.timedelta(days=2)
        if not datetime.date(1900, 1, 1) <= visit_date <= two_days_from_now:
            # We're lying a little here since we give a 2-day allowance for
            # timezone differences (ie: visit date _can_ be in the future)
            raise custom_errors.ValidationError(
                "visit date must be no earlier January 1, 1900 and cannot be "
                "in the future")

        return visit_date

    @sqlalchemy.orm.validates("comment")
    @not_none
    def validate_comment(self, _key, comment):
        if len(comment) <= 1:
            raise custom_errors.ValidationError(
                "comment must be more than 1 character")

        return comment

    @sqlalchemy.orm.validates("rating")
    @not_none
    def validate_rating(self, _key, rating):
        if not 0 <= rating <= 5:
            raise custom_errors.ValidationError(
                "rating must be between 0 and 5 inclusive")

        return rating
