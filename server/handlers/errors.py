import werkzeug

from app import app
import custom_errors


@app.errorhandler(custom_errors.ValidationError)
def validation_error(err):
    return {
        "result": "error",
        "message": err.message,
    }


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def otherwise_unhandled_error(err):
    return {
        "result": "error",
        "message": "An unexpected error occurred."
    }
