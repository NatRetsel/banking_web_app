import unittest
from app import create_app, db

class RoutesTestCase(unittest.TestCase):
    def setUp(self)->None:
        """
        Create an environment for the test that is close to a running application. 
        Application is configured for testing and context is activated to ensure that tests have access to current_app like requests do.
        Brand new database gets created for tests with create_all().
        """
        self.app = create_app('testing')
        self.app = self.app.test_client()
        db.create_all()
    
    def test_home_page(self)->None:
        """
        Given a test client
        When a get request is made to the home page
        Then validate the page exist by asserting the response code to be 200.
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    
    def test_index_page(self)->None:
        """
        Given a test client
        When a get request is made to the index page
        Then validate the page exist by asserting the response code to be 200.
        """
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)
    
    
    def test_register_page(self)->None:
        """
        Given a test client
        When a get request is made to the register page
        Then validate the page exist by asserting the response code to be 200.
        """
        response = self.app.get('/auth/register')
        self.assertEqual(response.status_code, 200)
    
    
    def test_login_page(self)->None:
        """
        Given a test client
        When a get request is made to the login page
        Then validate the page exist by asserting the response code to be 200.
        """
        response = self.app.get('/auth/login')
        self.assertEqual(response.status_code, 200)