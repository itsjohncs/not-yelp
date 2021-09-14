from functools import wraps

import flask

import custom_errors
from models.accounts import Account


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        account_id = flask.session.get("logged_in_account_id")
        if account_id:
            account = Account.query.filter_by(id=account_id).first()
            if account:
                flask.g.account = account  # pylint: disable=E0237
                return func(*args, **kwargs)

        raise custom_errors.AuthorizationError()

    return inner
