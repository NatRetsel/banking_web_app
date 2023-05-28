import pytest
from app import create_app
from app import db as _db


@pytest.fixture(scope='session')
def app(request):
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app
        

@pytest.fixture(scope='session')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def db(app, request):

    def teardown():
        _db.drop_all()
        
    _db.app = app
    _db.create_all()
    
    request.addfinalizer(teardown)

    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session