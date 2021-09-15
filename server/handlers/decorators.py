from functools import wraps

import flask

from models.accounts import has_permission
import custom_errors


def login_required(*, need_permissions=()):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if flask.g.account:
                for permission in need_permissions:
                    if not has_permission(flask.g.account, permission):
                        raise custom_errors.PermissionError(permission)

                return func(*args, **kwargs)
            else:
                raise custom_errors.AuthorizationError()

        return inner

    return decorator
