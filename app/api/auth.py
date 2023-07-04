from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.api.errors import error_response


# Basic verification with Flask's HTTPBasicAuth
# Requirements 1.) Function to verify username or equivalent and password 
#               2.) Function to return error response
basic_auth = HTTPBasicAuth()

# Protecting routes with tokens with Flask's HTTPTokenAuth
# Similarly requirements 1.) Function to provide token verification
#                        2.) Function to return error response
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email, password):
    # Requirement 1 for basic verification with Flask's HTTPBasicAuth
    # Authentication flow configured with the decorator
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    # Requirement 2 for basic verification with Flask's HTTPBasicAuth
    # Authentication flow configured with the decorator
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    # Requirement 1 for token verification with Flask's HTTPTokenAuth
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    # Requirement 2 for token verification with Flask's HTTPTokenAuth
    return error_response(status)