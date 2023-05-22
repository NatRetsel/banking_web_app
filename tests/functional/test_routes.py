
def test_home_page(client):
    """
    GIVEN a Flask appliucation configured for testing
    WHEN the '/' or '/index' page is requested (GET)
    THEN check that the response is valid
    """
    
    
    
    response = client.get('/')
    assert response.status_code == 200
    assert b"<h1>Hello </h1>" in response.data

    