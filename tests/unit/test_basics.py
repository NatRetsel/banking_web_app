import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create an environment for the test that is close to a running application. 
        Application is configured for testing and context is activated to ensure that tests have access to current_app like requests do.
        Brand new database gets created for tests with create_all().
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self) -> None:
        """
        Removes application context and database after testing.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_app_exists(self):
        """
        Given app context configured for testing
        When unittest is invoked
        Then check if the application instance exist
        """
        self.assertFalse(current_app is None)
    
    def test_app_is_testing(self):
        """
        Given app context configured for testing
        When unittest is invoked
        Then check if the application configuration is set to testing.
        """
        self.assertTrue(current_app.config['TESTING'])
     
    