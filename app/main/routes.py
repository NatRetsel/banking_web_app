from flask import render_template, session, Response
from . import main

@main.route('/')
@main.route('/index')
def index() -> Response:
    """Index / Home route for the app. 
    Displays user's first name if logged in by retrieving it from the session, else Npme
    Returns:
        Response: index.html
    """
    
    first_name = session.get('first_name')
    return render_template('index.html', first_name=first_name)