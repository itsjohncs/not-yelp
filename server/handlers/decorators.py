from functools import wraps

import flask

import custom_errors


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if flask.g.account:
            return func(*args, **kwargs)
        else:
            raise custom_errors.AuthorizationError()

    return inner
