from functools import wraps

import custom_errors


def not_none(func):
    """Ensures that a field is not None.

    This can be used to wrap a SQLAlchemy validation function.

        @sqlalchemy.orm.validates("foobar")
        @not_none
        def validate_comment(self, _key, foobar):
            if len(foobar) <= 1:
                raise custom_errors.ValidationError(
                    "foobar must be more than 1 character")

            return foobar
    """
    @wraps(func)
    def inner(self, key, value):
        if value is None:
            raise custom_errors.ValidationError(
                f"a value for {key} must be given")

        return func(self, key, value)

    return inner
