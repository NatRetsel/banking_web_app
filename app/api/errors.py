from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    """Custom error response
        - Gets the status code from HTTP protocol status code
        - Optional message from the developers for the accompanying status code
        - Piece a JSON object
    Args:
        status_code (HTTP status code): HTTP protocol status code
        message (str, optional): Custom message for error. Defaults to None.

    Returns:
        JSON error response: in the format of
            {
                "error": "short error description",
                "message": "error message (optional)"
            }
    """
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(400, message)