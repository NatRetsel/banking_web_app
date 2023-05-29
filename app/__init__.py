import os
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))


bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login.init_app(app)
    
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app
    
