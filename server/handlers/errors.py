import werkzeug

from app import app
import custom_errors


@app.errorhandler(custom_errors.ValidationError)
def validation_error(err):
    return {
        "result": "error",
        "message": err.message,
    }, 400


@app.errorhandler(custom_errors.PermissionError)
def permission_error(err):
    return {
        "result": "error",
        "message": err.message,
    }, 401


@app.errorhandler(custom_errors.AuthorizationError)
def authorization_error(_err):
    return {
        "result": "error",
        "message": "You are not authorized to access this resource.",
    }, 401


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def otherwise_unhandled_error(_err):
    return {
        "result": "error",
        "message": "An unexpected error occurred."
    }, 500
