import datetime

import sqlalchemy
from sqlalchemy.sql.expression import select, update
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app import db
import custom_errors
from models.model_ids import generate_id
from models.decorators import not_none
from models.accounts import Account
from models.restaurants import Restaurant


class Review(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    visit_date = db.Column(db.Date(), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    author = db.Column(db.ForeignKey(Account.id), nullable=False)
    restaurant = db.Column(db.ForeignKey(Restaurant.id), nullable=False,
                           index=True)
    restaurant_obj = relationship(Restaurant)
    reply_author = db.Column(db.ForeignKey(Account.id))
    reply_comment = db.Column(db.Text())

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

    @sqlalchemy.orm.validates("restaurant")
    @not_none
    def validate_restaurant(self, _key, restaurant):
        # @not_none takes care of the only validation we'll do at this level
        return restaurant

    @sqlalchemy.orm.validates("reply_comment")
    def validate_reply_comment(self, _key, reply_comment):
        if len(reply_comment) <= 1:
            raise custom_errors.ValidationError(
                "reply_comment must be more than 1 character")

        return reply_comment

    def to_serializable(self):
        return {
            "id": self.id,
            "visit_date": self.visit_date,
            "comment": self.comment,
            "rating": self.rating,
            "author": self.author,
            "restaurant": self.restaurant,
            "reply_author": self.reply_author,
            "reply_comment": self.reply_comment,
        }


@db.event.listens_for(Review, "after_insert")  # pylint: disable=E1101
@db.event.listens_for(Review, "after_update")  # pylint: disable=E1101
def update_restaurant_on_review_insert(_mapper, connection, target):
    target_rating_changed = (
        sqlalchemy.inspect(target).attrs.rating
            .history.has_changes())
    if not target_rating_changed:
        return

    # Getting the average without race conditions would take some work but
    # fortunately the average being slightly off seems acceptable.
    result = connection.execute(
        select(func.avg(Review.rating))
            .filter_by(restaurant=target.restaurant)).all()
    average_rating = result[0][0]

    connection.execute(
        update(Restaurant)
            .where(Restaurant.id == target.restaurant)
            .values(average_rating=average_rating))
