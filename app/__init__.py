import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from app import routes