import datetime

import flask
import sqlalchemy

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
@login_required()
def get_reviews(restaurant):
    return {
        "result": "success",
        "reviews": Review.query.filter_by(restaurant=restaurant).all(),
    }
