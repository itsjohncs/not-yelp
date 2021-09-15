import datetime

import flask

from app import app, db
from models.reviews import Review
from handlers.decorators import login_required
import custom_errors


@app.route("/api/create-review", methods=["POST"])
@login_required
def create_review():
    visit_date = flask.request.json.get("visit_date")
    try:
        parsed_visit_date = datetime.date.fromisoformat(visit_date)
    except ValueError as err:
        raise custom_errors.ValidationError(
            "visit date must be in format YYYY-MM-DD (per ISO 8601)") from err

    comment = flask.request.json.get("comment")
    rating = flask.request.json.get("rating")

    review = Review(visit_date=parsed_visit_date, comment=comment,
                    rating=rating, author=flask.g.account.id)
    db.session.add(review)
    db.session.commit()

    return {
        "result": "success",
        "id": review.id,
    }
