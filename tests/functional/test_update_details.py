import unittest
import re
from app import create_app, db
from app.models import User, Role, Transactions, TransactionType

class UpdateCase(unittest.TestCase):
    
    
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
        TransactionType.insert_transaction_types()
        self.client = self.app.test_client(use_cookies=True)
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    
    def test_update_email_success(self)->None:
        """
        Register, Login, Change email
        Given a test client
        When a mock user creates an account, logs in and change email address successfully
        Then 
            - verify that the updated email is in the user row in database
            - user is able to login with new email but not old email
        
        
        """
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the new account
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
        
        # change email
        response = self.client.post('/auth/update', data={
            'new_email': 'devonedoe2@email.com',
            'new_email_2': 'devonedoe2@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        account_owner = db.session.query(User).filter_by(id=1).first()
        self.assertEqual(account_owner.email,'devonedoe2@email.com')
        
        # logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        
        # fail login with old email
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertTrue(re.search('Invalid email or password',
                    response.get_data(as_text=True)))
        
        
        # success login with new email
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe2@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
    

    def test_update_email_fail(self)->None:
        """
        Register, Login, Change email
        Given a test client
        
        1.) Same email address as before
        When a mock user creates an account, logs in and change email address with the same email
        Then 
            - verify that email is not updated in the database
        
        2.) Attempt to change email to that of another user
        When a mock user creates an account, logs in and change email address with the same email
        Then 
            - verify that email is not updated in the database for both accounts
        
        """
        # Account 1
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # Account 2
        response = self.client.post('/auth/register', data={
            'first_name': 'devtwo',
            'last_name': 'doe',
            'email': 'devonedoe2@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        
        # Scenario 1
        # log in with the new account 1
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
        
        # change email with same email address
        response = self.client.post('/auth/update', data={
            'new_email': 'devonedoe@email.com',
            'new_email_2': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        account_owner = db.session.query(User).filter_by(id=1).first()
        self.assertEqual(account_owner.email,'devonedoe@email.com')
        
        # Scenario 2
        # change email with email address of another user
        response = self.client.post('/auth/update', data={
            'new_email': 'devonedoe2@email.com',
            'new_email_2': 'devonedoe2@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        account_owner = db.session.query(User).filter_by(id=1).first()
        self.assertEqual(account_owner.email,'devonedoe@email.com')
    
    
    def test_change_password_success(self) -> None:
        """
        Register, Login, Change password
        Given a test client
        When a mock user creates an account, logs in and change password successfully
        Then 
            - verify that password hash is updated in database
            - user is able to log out and then login with the new password but not old password
        
        """
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the new account 
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
        
        # change password
        response = self.client.post('/auth/change_password', data={
            'old_password': 'testpassword',
            'new_password': 'testpassword2',
            'new_password_2': 'testpassword2'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # verify password
        account_owner = db.session.query(User).filter_by(id=1).first()
        self.assertTrue(account_owner.check_password('testpassword2'))
        
        # logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # log in with the old password (expected unsuccessful) 
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertTrue(re.search('Invalid email or password',
                    response.get_data(as_text=True)))
        
        
        # log in with the new password (expected unsuccessful) 
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword2'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
        
    
    
    def test_change_password_fail(self) -> None:
        """
        Register, Login, Change password
        Given a test client
        
        1.) Same password as before
        When a mock user creates an account, logs in and change password with the same password
        Then 
            - verify that password is not updated in the database
        
        """
        
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the new account 
        response = self.client.post('/auth/login', data={
            'email': 'devonedoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devone', response.data)
        
        # change password
        response = self.client.post('/auth/change_password', data={
            'old_password': 'testpassword',
            'new_password': 'testpassword',
            'new_password_2': 'testpassword'
        }, follow_redirects=True)
        self.assertTrue(re.search('Please enter a password different from the previous one',
                    response.get_data(as_text=True)))
        
        # verify old password
        account_owner = db.session.query(User).filter_by(id=1).first()
        self.assertTrue(account_owner.check_password('testpassword'))