from flask import jsonify
from app import db
from app.api import api
from app.api.auth import basic_auth, token_auth

@api.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    # Produce a token after verification authentication.
    # Decorated with @basic_auth from HTTPBasicAuth instance.
    # Instructs Flask-HTTPAuth to verify authentication and only allow the function to run when the provided credentials are valid. 
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})


@api.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    # Revokes a token after verification authentication.
    # Decorated with @basic_auth from HTTPBasicAuth instance.
    # Instructs Flask-HTTPAuth to verify authentication and only allow the function to run when the provided credentials are valid.
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204