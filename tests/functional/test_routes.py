import json
from app.models import User

def test_home_page(client):
    """
    GIVEN a Flask appliucation configured for testing
    WHEN the '/' or '/index' page is requested (GET)
    THEN check that the response is valid (200) and the body contains"<h1>Hello </h1>"
    """
    
    response = client.get('/')
    assert response.status_code == 200
    assert b"<h1>Hello </h1>" in response.data
    
    response = client.get('/index')
    assert response.status_code == 200
    assert b"<h1>Hello </h1>" in response.data


def test_login_page(client):
    """
    GIVEN a Flask appliucation configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid (200)
    """
    response = client.get('/login')
    assert response.status_code == 200


def test_register_page(client):
    """
    GIVEN a Flask appliucation configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid (200)
    """
    response = client.get('/register')
    assert response.status_code == 200


def test_register(client,db):
    
    
    response = client.post('/register', 
                            data = json.dumps(dict(
                                        first_name="testfirstname",
                                        last_name="testlastname",
                                        email="testmail@email.com",
                                        password="testpassword",
                                        password2="testpassword"
                                    )), follow_redirects=True)
    assert response.status_code == 200
    added_user = User.query.filter(User.email=="testmail@email.com").first()
    assert added_user
    db.delete(added_user)
    db.commit()
    
    
    
        
    