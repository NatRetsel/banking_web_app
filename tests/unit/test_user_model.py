import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        """
        Given a user model
        When the password is supplied
        Then verify that the set password function is working as intended (only password hash is stored)
        """
        u = User()
        password = 'cat'
        u.set_password(password)
        self.assertTrue(password != u.password_hash)
    
    def test_no_password_getter(self):
        """
        Given a user model
        When a request is made to retrieve the user's password
        Then verify that the user's password is not a readable attribute
        """
        u = User()
        u.set_password('cat')
        with self.assertRaises(AttributeError):
            u.password
    
    def test_password_verification(self):
        """
        Given a user model
        When a user's password is set
        Then verify that the check_password method is working as intended.
        """
        u = User()
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))
    
    def test_pasword_salts_are_random(self):
        """
        Given two user models
        When both user's passwords are set to the same 
        Then verify that their hashes are different
        """
        u = User()
        u.set_password('cat')
        u2 = User()
        u2.set_password('cat')
        self.assertTrue(u.password_hash != u2.password_hash)
        