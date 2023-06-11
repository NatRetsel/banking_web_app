import os
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

basedir = os.path.abspath(os.path.dirname(__file__))

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

bootstrap = Bootstrap()
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'
migrate = Migrate()
db = SQLAlchemy(metadata=metadata)


def create_app(config_name):
    # Application factory
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app
    
