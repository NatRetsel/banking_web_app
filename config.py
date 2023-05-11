import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    
    SQLALCHEMY_DATABASE_URI = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'hard to guess sting' # used as an encrpyption or signing key. Flask uses this key in its mechanism for csrf protection
