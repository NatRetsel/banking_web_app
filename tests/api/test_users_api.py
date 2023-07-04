import unittest
from unittest.mock import patch
from app import create_app, db
from app.models import User, Role, TransactionType
from flask import jsonify
import json, requests
from base64 import b64encode

class UsersAPITestCase(unittest.TestCase):
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
    
    
    def test_create_account_from_api_success(self):
        """
        Given an API for account creation
        When a post request is made with the appropriate JSON keyword fields
        Then verify that the response indicates that the account has been created and a JSON representation of the user account is received
        """
        url = 'http://localhost:5000/api/users'
        expected_response = {
            'id':1,
            "first_name": 'loreum',
            "last_name": 'ipsum',
            "email": 'loreumipsum@email.com',
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"    
        }
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertTrue('id' in response.json)
        self.assertTrue('first_name' in response.json)
        self.assertTrue('last_name' in response.json)
        self.assertTrue('email' in response.json)
        self.assertTrue('accounts' in response.json)
        self.assertTrue('transactions' in response.json)
        self.assertEqual(response.json, expected_response)
    
    
    def test_create_account_from_api_fail(self):
        """
        Given an API for account creation
        
        # 1
        When a POST request is made with the appropriate JSON keyword fields but with an email that is already taken
        Then verify that the response indicates a bad request and the returned json:
        {
            'error': 'Bad Request',
            'message': 'please use a different email address'   
        }
        
        # 2
        When a POST request is made with invalid JSON keyword fields
        Then verify that the response indicates a bad request and returned json:
        {
            'error': 'Bad Request',
            'message': 'must include first name, last name, email and password fields'   
        }
        """
        url = 'http://localhost:5000/api/users'
        
        data1 = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        # 1
        data2 = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        expected_response1 = {
            'error': 'Bad Request',
            'message': 'please use a different email address'   
        }
        response = self.client.post(url, json=data1)
        response = self.client.post(url, json=data2)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response1)
        
        # 2
        data2 = {}
        expected_response2 = {
            'error': 'Bad Request',
            'message': 'must include first name, last name, email and password fields'   
        }
        response = self.client.post(url, json=data2)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response2)
    
    
    def test_login_auth_for_token(self):
        """
        Given an API for token generation
        When a POST request is made with the appropriate authentication fields
        Then verify that the response indicates that the token generation is successful and is in the JSON response
        """
        
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth token   
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in response.json)
    
    
    def test_update_email_api_success(self):
        """
        Given an API for updating user email and a valid user account
        When a PUT request is made with the appropriate authentication fields and valid new email
        Then verify that the response indicates that the email change is successful and is in the JSON response
        """
        
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth token
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # Update email
        url_update_email = 'http://localhost:5000/api/users/1/change_email'
        data = {
            'new_email': 'loreumipsum2@email.com'
        }
        
        expected_response_json = {
            'id':1,
            "first_name": 'loreum',
            "last_name": 'ipsum',
            "email": 'loreumipsum2@email.com',
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
        
        response = self.client.put(url_update_email, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response_json)
    
    
    def test_update_email_api_fail(self):
        """
        Given an API for updating user email and a valid user account
        
        # 1 invalid auth field
        When a PUT request is made with invalid authentication fields
        Then verify that the response indicates unauthorized (401)
        
        # 2 invalid new email
        When a PUT request is made with the appropriate authentication fields and a valid new email
        Then verify that the response indicate a bad request and the message to use a different email
        """
        
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data1 = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data1)
        
        # 1 update email with invalid auth field
        url_update_email = 'http://localhost:5000/api/users/1/change_email'
        data = {
            'new_email': 'loreumipsum2@email.com'
        }
        token = ''
        response = self.client.put(url_update_email, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 401)
        
        # 2 update email with valid auth field but invalid new email
        
        # Register new user
        url = 'http://localhost:5000/api/users'
        
        data2 = {
            'first_name': 'loreumum',
            'last_name': 'ipsumum',
            'email': 'loreumipsum2@email.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, json=data2)
        
        # Request Auth Token for account 1
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # Update email of account 1
        expected_response = {
            'error': 'Bad Request',
            'message': 'Please use a different email'   
        }
        response = self.client.put(url_update_email, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)
            
    
    def test_change_password_api_success(self):
        """
        Given an API for updating user password and a valid user account
        When a PUT request is made with the appropriate authentication fields and valid new password
        Then verify that the response indicates that the password change is successful and is in the JSON response
        AND when a request is made for the auth token, it matches the earlier provided token
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth token
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token1 = response.json['token']
        
        # Update password
        url_update_password = 'http://localhost:5000/api/users/1/change_password'
        data = {
            'old_password': 'testpassword',
            'new_password': 'testpassword2'
        }
        
        expected_response_json = {
            'id':1,
            "first_name": 'loreum',
            "last_name": 'ipsum',
            "email": 'loreumipsum@email.com',
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
        
        response = self.client.put(url_update_password, headers={'Authorization': 'Bearer '+token1}, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response_json)
        
        # Able to request for auth token and it matches the previous token as it hasn't expire
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword2'))
        token2 = response.json['token']
        self.assertEqual(token1, token2)
    
    
    def test_change_password_api_fail(self):
        """
        Given an API for updating user password and a valid user account
        
        # 1 
        When a PUT request is made with invalid authentication fields
        Then verify that the response indicates unauthorized (401)
        
        # 2
        When a PUT request is made with valid authentication fields but with the same password as current password
        Then verify that the response indicates a bad request and the message "Your password cannot be the same as your old password"
        
        # 3 
        When a PUT request is made with valid authentication fields but a incorrect current password is supplied
        Then verify that the response indicates a bad request and the message "Invalid credentials"
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 update password with invalid auth field
        url_update_password = 'http://localhost:5000/api/users/1/change_password'
        data = {
            'old_password': 'testpassword',
            'new_password': 'testpassword2'
        }
        token = ''
        response = self.client.put(url_update_password, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 401)
        
        # 2 update password with valid auth field but with the same password as current password
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # Update password with the same password
        data = {
            'old_password': 'testpassword',
            'new_password': 'testpassword'
        }
        expected_response = {
            'error': 'Bad Request',
            'message': 'Your password cannot be the same as your old password'   
        }
        response = self.client.put(url_update_password, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)
        
        # 3 update password with valid auth field but with incorrect current password
        data = {
            'old_password': 'testpassword2',
            'new_password': 'testpassword3'
        }
        expected_response = {
            'error': 'Bad Request',
            'message': 'Invalid credentials'   
        }
        response = self.client.put(url_update_password, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)
    
    
    def test_get_user_api_success(self):
        """
        Given an API for request user information and a valid user account
        When a GET request is sent with a valid authentication credentials
        Then verify that the user information is returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET user information
        url_get_user = 'http://localhost:5000/api/users/1'
        response = self.client.get(url_get_user, headers={'Authorization': 'Bearer '+token})
        
        # Verify response
        expected_json = {
            'id':1,
            "first_name": 'loreum',
            "last_name": 'ipsum',
            "email": 'loreumipsum@email.com',
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
        
    
    def test_get_user_api_fail(self):
        """
        Given an API for request user information and a valid user account
        
        # 1
        When a GET request is sent for a user using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a GET request is sent for a different user / invalid with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # GET user information with invalid token
        token = ''
        url_get_user = 'http://localhost:5000/api/users/1'
        response = self.client.get(url_get_user, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)
        
        # 2 sent for a different user with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET different user information with valid token
        url_get_user = 'http://localhost:5000/api/users/2'
        response = self.client.get(url_get_user, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 403)
        
    
    def test_get_user_account_api_success(self):
        """
        Given an API for request user's specific bank account information and a valid user account
        When a GET request is sent with a valid authentication credentials
        Then verify that the user's bank account information is returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET user account information
        url_get_user_account = 'http://localhost:5000/api/users/1/accounts/1'
        response = self.client.get(url_get_user_account, headers={'Authorization': 'Bearer '+token})
        
        # Verify response
        expected_json = {
            "account_num": 1,
            "balance": 0,
            "owner": 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
    
    
    def test_get_user_account_api_fail(self):
        """
        Given an API for request a user's specific bank account information and a valid user account
        
        
        # 1
        When a GET request is sent for the user bank account using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a GET request is sent for a different user bank account / invalid with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        # 3
        When a GET request is sent for an invalid user bank account 
        Then verify that the response is not found (404)
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # GET user;s bank account information with invalid token
        token = ''
        url_get_user_bank_account = 'http://localhost:5000/api/users/1/accounts/1'
        response = self.client.get(url_get_user_bank_account, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)
        
        # 2 sent for a different user's bank account with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET different user information with valid token
        url_get_user_bank_account = 'http://localhost:5000/api/users/2/accounts/2'
        response = self.client.get(url_get_user_bank_account, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 403)
        
        # 3 sent for non existent account under user
        url_get_user_bank_account = 'http://localhost:5000/api/users/1/accounts/2'
        response = self.client.get(url_get_user_bank_account, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 404)
    
    
    def test_get_user_accounts_api_success(self):
        """
        Given an API for request all of user's bank accounts information and a valid user account
        When a GET request is sent with a valid authentication credentials
        Then verify that the all user's bank accounts information are returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET user account information
        url_get_user_account = 'http://localhost:5000/api/users/1/accounts'
        response = self.client.get(url_get_user_account, headers={'Authorization': 'Bearer '+token})
        
        # Verify response
        expected_json = {
            "_meta": {
                "num_accounts": 1,
                "total_balance": 0
            },
            
            "accounts": [
                {
                    "account_num":1,
                    "balance": 0,
                    "owner": 1
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
    
    
    def test_get_user_accounts_api_fail(self):
        """
        Given an API for request all of a user's bank accounts information and a valid user account
        
        
        # 1
        When a GET request is sent for all of the user's bank accounts using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a GET request is sent for all of a different user's bank account / invalid user with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # GET user's bank accounts information with invalid token
        token = ''
        url_get_user_bank_accounts = 'http://localhost:5000/api/users/1/accounts'
        response = self.client.get(url_get_user_bank_accounts, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)
        
        # 2 sent for a different user's bank accounts with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET different user bank accounts information with valid token
        url_get_user_bank_accounts = 'http://localhost:5000/api/users/2/accounts'
        response = self.client.get(url_get_user_bank_accounts, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 403)
        
    
    def test_get_user_transaction_api_success(self):
        """
        Given an API for request user's specific transaction information and a valid user account
        When a GET request is sent with a valid authentication credentials
        Then verify that the user's specific transaction information is returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET user account information
        url_get_user_transaction = 'http://localhost:5000/api/users/1/transactions/1'
        response = self.client.get(url_get_user_transaction, headers={'Authorization': 'Bearer '+token})
        
        # Verify response
        expected_json = {
            "id": 1,
            "amount": 0,
            "from": 'loreum ipsum',
            "from_acc": 1,
            "to": 'loreum ipsum',
            "to_acc": 1,
            "type": "New Account"
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
    
    
    def test_get_user_transaction_api_fail(self):
        """
        Given an API for request all of a user's specific transaction information and a valid user account
        
        
        # 1
        When a GET request is sent for the user's specific transaction information using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a GET request is sent for a different user's specific transaction information / invalid user with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        # 3
        When a GET request is sent for the user's nonexistent transaction 
        Then verify that the response is not found (404)
        
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # GET user's transaction information with invalid token
        token = ''
        url_get_user_transaction = 'http://localhost:5000/api/users/1/transactions/1'
        response = self.client.get(url_get_user_transaction, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)
        
        # 2 sent for a different user's transaction with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET different user's transaction information with valid token
        url_get_user_transaction = 'http://localhost:5000/api/users/2/transactions/2'
        response = self.client.get(url_get_user_transaction, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 403)
        
        # 3 sent for user's non existent transaction
        url_get_user_transaction = 'http://localhost:5000/api/users/1/transactions/2'
        response = self.client.get(url_get_user_transaction, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 404)
    
    
    def test_get_user_transactions_api_success(self):
        """
        Given an API for request for all of user's transaction information and a valid user account
        When a GET request is sent with a valid authentication credentials
        Then verify that all of user's transaction information is returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET user account information
        url_get_user_transactions = 'http://localhost:5000/api/users/1/transactions'
        response = self.client.get(url_get_user_transactions, headers={'Authorization': 'Bearer '+token})
        
        # Verify response
        expected_json = {
            "_meta": {
                "total_transactions":1
            },
            "transactions": [
                {
                    "id": 1,
                    "amount": 0,
                    "from": 'loreum ipsum',
                    "from_acc": 1,
                    "to": 'loreum ipsum',
                    "to_acc": 1,
                    "type": "New Account"
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
    
    
    def test_get_user_transactions_api_fail(self):
        """
        Given an API for request all of a user's transaction information and a valid user account
        
        
        # 1
        When a GET request is sent for the user's transaction information using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a GET request is sent for a different user's entire transaction information / invalid user with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # GET user's transaction information with invalid token
        token = ''
        url_get_user_transactions = 'http://localhost:5000/api/users/1/transactions'
        response = self.client.get(url_get_user_transactions, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)
        
        # 2 sent for a different user's transaction with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # GET different user's entire transaction information with valid token
        url_get_user_transactions = 'http://localhost:5000/api/users/2/transactions'
        response = self.client.get(url_get_user_transactions, headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 403)
        
    
    
    def test_deposit_api_success(self):
        """
        Given an API for depositing money into a user's specified bank account and a valid user account
        When a POST request is sent with a valid authentication credentials
        Then verify that the user's specified bank account is updated with the deposit amount and both the account and transaction are returned
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # POST user deposit
        data = {
            "deposit_amount":3
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/1/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        
        # Verify response
        expected_json = {
            "account": {
                "account_num": 1,
                "balance": 3,
                "owner": 1
            },
            "transaction": {
                "amount": 3,
                "from": 'loreum ipsum', 
                "from_acc": 1,
                "id": 2,
                "to": 'loreum ipsum',
                "to_acc": 1,
                "type": "Deposit"
            }
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, expected_json)
    
    
    def test_deposit_api_fail(self):
        """
        Given an API for depositing money into a user's bank account and a valid user account
        
        
        # 1
        When a POST request is sent for the user's bank account using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a POST request is sent for a different user's bank account / invalid user with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        # 3
        When a POST request is sent for the user's bank account using valid authentication credentials but invalid deposit amount
        Then verify that the response is bad request (400) with message "Please enter a valid deposit amount"
        
        # 4
        When a POST request is sent for the user's nonexistent bank account using valid authentication credentials
        Then verify that the response is bad request (400) with message "Invalid credentials"
         
        """
        # Register user
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'loreum',
            'last_name': 'ipsum',
            'email': 'loreumipsum@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # 1 using invalid authentication credentials
        # POST to user's bank account with invalid token
        token = ''
        data = {
            'deposit_amount': 3
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/1/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 401)
        
        
        # 2 sent for a different user's transaction with using different valid authentication credentials
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('loreumipsum@email.com', 'testpassword'))
        token = response.json['token']
        
        # POST to different user's bank account with valid token
        url_post_deposit = 'http://localhost:5000/api/users/2/accounts/2/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 403)
        
        # 3 sent for the user's bank account but invalid deposit amount
        data = {
            'deposit_amount': -3
        }
        expected_json = {
            'error': 'Bad Request',
            'message': 'Please enter a valid deposit amount'
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/1/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_json)
        
        # 4 sent for a user's nonexistent bank account
        data = {
            'deposit_amount': 3
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/3/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 404)
    
    
    def test_transfer_api_success(self):
        """
        Given an API for transfering money into a user's specified bank account and 2 valid accounts
        When a POST request is sent with a valid authentication credentials
        Then verify that both bank accounts are updated with the transfer amount and both the account and transaction are returned
        """
        # Register user 1
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Register user 2
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 1
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('janedoe@email.com', 'testpassword'))
        token = response.json['token']
        
        # POST user deposit account 1
        data = {
            "deposit_amount":10
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/1/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        
        # POST transfer from account 1 to account 2
        data = {
            "to_account_num": 2,
            "amount":3
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/1/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        
        # Verify response for account 1
        expected_json = {
            "account": {
                "account_num": 1,
                "balance": 7,
                "owner": 1
            },
            "transaction": {
                "amount": 3,
                "from": 'Jane Doe', 
                "from_acc": 1,
                "id": 4,
                "to": 'John Doe',
                "to_acc": 2,
                "type": "Transfer"
            }
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, expected_json)
        
        # Verify response for account 2
        # Request token auth
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('johndoe@email.com', 'testpassword'))
        token = response.json['token']
        
        # Get account
        url_user_account = 'http://localhost:5000/api/users/2/accounts/2'
        response = self.client.get(url_user_account, headers={'Authorization': 'Bearer '+token})
        expected_json = {
            "account_num": 2,
            "balance": 3,
            "owner": 2
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_json)
        
    
    def test_transfer_api_fail(self):
        """
        Given an API for transferring money into a user's bank account and two valid user accounts
        
        
        # 1
        When a POST request to transfer into another user's bank account using invalid authentication credentials 
        Then verify that the response is unauthorized (401)
        
        # 2
        When a POST request to transfer as another user's bank account / invalid user with using different valid authentication credentials 
        Then verify that the response is forbidden (403)
        
        # 3
        When a POST request to transfer into another user's bank account using valid authentication credentials but invalid transfer amount
        Then verify that the response is bad request (400) with message "Please enter a valid transfer amount"
        
        # 4
        When a POST request transfer into another user's nonexistent bank account using valid authentication credentials
        Then verify that the response is not found (404) 
        
        # 5
        When a POST request transfer using a nonexistent bank account
        Then verify that the response is not found (404) 
        
        # 5
        When a POST request transfer using an invalid bank account
        Then verify that the response is bad request (400) with message 'Invalid credentials'
         
        """
        # Register user 1
        url = 'http://localhost:5000/api/users'
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Register user 2
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@email.com',
            'password': 'testpassword'
        }
        
        response = self.client.post(url, json=data)
        
        # Request Auth Token for account 1
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('janedoe@email.com', 'testpassword'))
        token = response.json['token']
        
        # POST user deposit account 1
        data = {
            "deposit_amount":10
        }
        url_post_deposit = 'http://localhost:5000/api/users/1/accounts/1/deposit'
        response = self.client.post(url_post_deposit, headers={'Authorization': 'Bearer '+token}, json=data)
        
        # 1 using invalid authentication credentials to transfer to account 2 from account 1
        # POST to user's bank account with invalid token
        token = ''
        data = {
            'to_account_num': 2,
            'amount': 3
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/1/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 401)
        
        
        # 2 transfer as another user's bank account with token auth for account 1
        # Request Auth Token for account 
        url_token = 'http://localhost:5000/api/tokens'
        response = self.client.post(url_token, auth=('janedoe@email.com', 'testpassword'))
        token = response.json['token']
        
        # POST as different user's bank account with with token auth for account 1
        data = {
            'to_account_num': 1,
            'amount': 3
        }
        url_post_transfer = 'http://localhost:5000/api/users/2/accounts/2/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 403)
        
        # 3 transfer to another user's bank account but invalid amount
        data = {
            'to_account_num': 2,
            'amount': 100
        }
        expected_json = {
            'error': 'Bad Request',
            'message': 'Please enter a valid transfer amount'
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/1/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_json)
        
        # 4 transfer to a user's nonexistent bank account
        data = {
            'to_account_num': 3,
            'amount': 3
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/1/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 404)
        
        # 5 Transfer to a user's account using a non existent account
        data = {
            'to_account_num': 2,
            'amount': 3
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/3/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 404)
        
        # 6 Transfer using invalid account
        data = {
            'to_account_num': 2,
            'amount': 3
        }
        expected_json = {
            'error': 'Bad Request',
            'message': 'Invalid credentials'
        }
        url_post_transfer = 'http://localhost:5000/api/users/1/accounts/2/transfer'
        response = self.client.post(url_post_transfer, headers={'Authorization': 'Bearer '+token}, json=data)
        self.assertEqual(response.status_code, 400)