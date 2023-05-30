from flask import render_template, session, Response
from . import main

@main.route('/')
@main.route('/index')
def index() -> Response:
    first_name = session.get('first_name')
    return render_template('index.html', first_name=first_name)