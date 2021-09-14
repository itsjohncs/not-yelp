import flask

from app import app, db
from handlers.decorators import login_required
from models.restaurants import Restaurant
import custom_errors


@app.route("/api/create-restaurant", methods=["POST"])
@login_required
def create_restaurant():
    title = flask.request.json.get("title")
    if not title:
        raise custom_errors.ValidationError("title is required")

    restaurant = Restaurant(title=title, owner=flask.g.account.id)
    db.session.add(restaurant)
    db.session.commit()

    return {
        "result": "success",
        "id": restaurant.id,
    }


@app.route("/api/restaurants")
@login_required
def get_restaurants():
    query = Restaurant.query

    owner = flask.request.args.get("owner")
    if owner:
        query = query.filter_by(owner=owner)

    return {
        "result": "success",
        "restaurants": query.all(),
    }
