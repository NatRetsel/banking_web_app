import unittest
from app import create_app, db
from app.models import User, Role, Accounts, Transactions, TransactionType

class TransactionsCase(unittest.TestCase):
    
    
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
        
        
    def test_new_account(self) -> None:
        """
        GIVEN a user who wish to create a new account
        WHEN said account is created
        THEN validate that default balance is set to 0, 
            transaction details
                - receiver and sender are the same
                - amount is 0
                - type is "New Account"
        """
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        account = db.session.query(Accounts).filter_by(account_num=1).first()
        self.assertEqual(account.account_owner.email, "devonedoe@email.com")
        self.assertEqual(account.balance, 0)
        
        transaction = db.session.query(Transactions).filter_by(receiver=account.account_num).first()
        self.assertEqual(transaction.receiver, account.account_num)
        self.assertEqual(transaction.amount, 0)
        self.assertEqual(transaction.transaction_type.name, "New Account")
    
    
    def test_deposit(self) -> None:
        """
        GIVEN a new account
        WHEN said account posts a deposit
        THEN validate that balance is set to amount deposited, 
            transaction details
                - receiver and sender are the same
                - amount is form.amount.data
                - type is "Deposit"
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
        
        response = self.client.post('/auth/deposit', data={
            'amount': 10
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        account = db.session.query(Accounts).filter_by(account_num=1).first()
        self.assertEqual(account.account_owner.email, "devonedoe@email.com")
        self.assertEqual(account.balance, 10)
        
        transaction = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).first()
        self.assertEqual(transaction.receiver, account.account_num)
        self.assertEqual(transaction.amount, 10)
        self.assertEqual(transaction.transaction_type.name, "Deposit")
        
        
    def test_successful_transfer(self) -> None:
        """
        GIVEN two accounts
        WHEN one account posts a transfer after a deposit
        THEN validate that balance is set to amount deposited - transfer for sender and + transfer for receiver
            transaction details
                - receiver and sender are the respective parties
                - amount is form.amount.data
                - type is "Transfer"
        """
        # Register account 1
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # Register account 2
        response = self.client.post('/auth/register', data={
            'first_name': 'devtwo',
            'last_name': 'doe',
            'email': 'devtwodoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the account 2
        response = self.client.post('/auth/login', data={
            'email': 'devtwodoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devtwo', response.data)
        
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, 'devtwodoe@email.com')
        self.assertEqual(account.balance, 0)
        
        # Deposit into account 2
        response = self.client.post('/auth/deposit', data={
            'amount': 10
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, "devtwodoe@email.com")
        self.assertEqual(account.balance, 10)
        
        # From account 2 transfer to account 1
        response = self.client.post('/auth/transfer', data={
            'recipient_acc_num': 1,
            'amount': 5
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, "devtwodoe@email.com")
        self.assertEqual(account.balance, 5)
        
        # Validate account 1's balance
        recipient_account = db.session.query(Accounts).filter_by(account_num=1).first()
        self.assertEqual(recipient_account.account_owner.email, "devonedoe@email.com")
        self.assertEqual(recipient_account.balance, 5)
        
        # Validate transaction details
        transaction = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).first()
        self.assertEqual(transaction.sender, account.account_num)
        self.assertEqual(transaction.receiver, recipient_account.account_num)
        self.assertEqual(transaction.amount, 5)
        self.assertEqual(transaction.transaction_type.name, "Transfer")
        
    
    def test_unsuccessful_transfer(self) -> None:
        """
        Insufficient balance
        GIVEN two accounts
        WHEN one account posts a transfer with insufficient balance
        THEN validate that no transaction took place
            - balance of both accounts remained unchanged
            - no record of such transaction -> latest transaction should be of type "New Account" or "Deposit" if deposit was made
        
        No such user
        GIVEN an account
        WHEN one account posts a transfer to a user who does not exist
        THEN validate that no transaction took place
            - balance of account remained unchanged
            - no record of such transaction -> latest transaction should be of type "New Account"
        """
        # Insufficient balance
        # Register account 1
        response = self.client.post('/auth/register', data={
            'first_name': 'devone',
            'last_name': 'doe',
            'email': 'devonedoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # Register account 2
        response = self.client.post('/auth/register', data={
            'first_name': 'devtwo',
            'last_name': 'doe',
            'email': 'devtwodoe@email.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # log in with the account 2
        response = self.client.post('/auth/login', data={
            'email': 'devtwodoe@email.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello devtwo', response.data)
        
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, 'devtwodoe@email.com')
        self.assertEqual(account.balance, 0)
        
        # Deposit into account 2
        response = self.client.post('/auth/deposit', data={
            'amount': 10
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, "devtwodoe@email.com")
        self.assertEqual(account.balance, 10)
        
        # From account 2 transfer to account 1
        response = self.client.post('/auth/transfer', data={
            'recipient_acc_num': 1,
            'amount': 11
        }, follow_redirects=True)
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, "devtwodoe@email.com")
        self.assertEqual(account.balance, 10)
        
        # Validate account 1's balance
        recipient_account = db.session.query(Accounts).filter_by(account_num=1).first()
        self.assertEqual(recipient_account.account_owner.email, "devonedoe@email.com")
        self.assertEqual(recipient_account.balance, 0)
        
        # Validate latest transaction details of "sender" account 2
        transaction = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).first()
        self.assertEqual(transaction.sender, account.account_num)
        self.assertEqual(transaction.receiver, account.account_num)
        self.assertEqual(transaction.amount, 10)
        self.assertEqual(transaction.transaction_type.name, "Deposit")
        
        # Validate latest transaction details of "receiver" account 1
        transaction = Transactions.query.filter((Transactions.receiver_account == recipient_account) | 
                                                 (Transactions.sender_account == recipient_account)).order_by(Transactions.date_time.desc()).first()
        self.assertEqual(transaction.sender, recipient_account.account_num)
        self.assertEqual(transaction.receiver, recipient_account.account_num)
        self.assertEqual(transaction.amount, 0)
        self.assertEqual(transaction.transaction_type.name, "New Account")
        
        
        # From account 2 transfer to non existent account
        response = self.client.post('/auth/transfer', data={
            'recipient_acc_num': 3,
            'amount': 5
        }, follow_redirects=True)
        account = db.session.query(Accounts).filter_by(account_num=2).first()
        self.assertEqual(account.account_owner.email, "devtwodoe@email.com")
        self.assertEqual(account.balance, 10)
        
        
        # Validate latest transaction details of "sender" account 2
        transaction = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).first()
        self.assertEqual(transaction.sender, account.account_num)
        self.assertEqual(transaction.receiver, account.account_num)
        self.assertEqual(transaction.amount, 10)
        self.assertEqual(transaction.transaction_type.name, "Deposit")
        
        