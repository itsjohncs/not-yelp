import datetime

import flask
import sqlalchemy
from sqlalchemy.orm import joinedload

from app import app, db
from models.reviews import Review
from models.accounts import Permission
from handlers.decorators import login_required
import custom_errors


@app.route("/api/create-review", methods=["POST"])
@login_required(need_permissions=[Permission.CREATE_REVIEW])
def create_review():
    visit_date = flask.request.json.get("visit_date")
    try:
        parsed_visit_date = datetime.date.fromisoformat(visit_date)
    except (ValueError, TypeError) as err:
        raise custom_errors.ValidationError(
            "visit date must be in format YYYY-MM-DD (per ISO 8601)") from err

    comment = flask.request.json.get("comment")
    rating = flask.request.json.get("rating")
    restaurant = flask.request.json.get("restaurant")

    review = Review(
        visit_date=parsed_visit_date,
        comment=comment,
        rating=rating,
        restaurant=restaurant,
        author=flask.g.account.id)
    db.session.add(review)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        raise custom_errors.ValidationError("restaurant does not exist") from e

    return {
        "result": "success",
        "id": review.id,
    }


@app.route("/api/restaurants/<restaurant>/reviews")
def get_reviews(restaurant):
    return {
        "result": "success",
        "reviews": Review.query.filter_by(restaurant=restaurant).all(),
    }


@app.route("/api/reviews/<review>/create-reply", methods=["POST"])
@login_required(need_permissions=[Permission.CREATE_REVIEW_REPLY])
def create_review_reply(review):
    review = (
        Review.query
            .filter_by(id=review)
            .options(joinedload(Review.restaurant_obj))
            .populate_existing()
            .with_for_update()
            .first())
    if not review:
        raise custom_errors.ValidationError("unknown review id")

    if ("admin" not in flask.g.account.roles and
            review.restaurant_obj.owner != flask.g.account.id):
        raise custom_errors.AuthorizationError(
            "you are not the owner of the restaurant")

    comment = flask.request.json.get("comment")
    review.reply_author = flask.g.account.id
    review.reply_comment = comment

    db.session.commit()

    return {
        "result": "success",
    }
