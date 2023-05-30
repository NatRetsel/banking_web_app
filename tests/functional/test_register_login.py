import unittest
from app import create_app, db
from app.models import User, Role

class RegisterLoginTestCase(unittest.TestCase):
    def setUp(self)->None:
        """
        Create an environment for the test that is close to a running application. 
        Application is configured for testing and context is activated to ensure that tests have access to current_app like requests do.
        Brand new database gets created for tests with create_all().
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_register_and_login(self)->None:
        """
        Register
        Given a test client
        When a mock user creates an account (POST request on register page)
        Then first check if the form is validated and data is pushed into the database by asserting the redirect to login page (302)
        
        Login
        Given a test client in the session where a new user has just created an account
        When the mock user logs in (POST request on login page)
        Then valdiate that the status code is 200 and the user login works by asserting the first name appears in the redirected index page.
        """
        response = self.client.post('/auth/register', data={
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the new account
        response = self.client.post('/auth/login', data={
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello loreum', response.data)
        
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        