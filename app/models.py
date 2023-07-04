from app import db, login
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login
import base64
from datetime import datetime, timedelta
import os

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    """Role SQlite ORM model
        Columns:
            - id (SQLite int): primary key
            - name (SQLite str64): role name in system (e.g. Admin, Moderator, User)
            - default (SQLite bool): Only one role is marked True (User)
        
    """
    __tablename__ = "roles_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role') # Adds role attribute to User model
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
    
    @staticmethod
    def insert_roles()->None:
        # Static method to push roles into database.
        roles = {'Administrator', 'Moderator', 'User'}
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
        
    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """User SQlite ORM model
        Columns:
            - id (SQLite int): primary key
            - first_name (SQLite str64): user first name
            - last_name (SQLite str64): user last name
            - email (SQLite str120): user email
            - password_hash (SQLite str128): user hashed password
            - role_id (SQLite int): user's role, mapped to Role table
            

    """
    
    __tablename__ = "users_table"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles_table.id'))
    accounts = db.relationship("Accounts", backref="account_owner")
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
    
    @property
    def password(self):
        """Raises AttributeError when password is queried for

        Raises:
            AttributeError: password is not a readable attribute
        """
        raise AttributeError('password is not a readable attribute')
    
    def set_password(self, password: str) -> None:
        """Stores user's password as a hashed value
            Reduces risk of compromising user information safety if we store password hash instead.
            Uses Werkzeug's security moduyle hashing. Default hashing method 'pbkdf2:sha256', salt length = 8

        Args:
            password (str): user input in the password field
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if input password matches the one stored in database as a hashed value.

        Args:
            password (str): user input in the password field

        Returns:
            bool: True if the input password matches the one stored in database as a hashed value.
        """
        return check_password_hash(self.password_hash, password)
    
    
    def get_token(self, expires_in=3600):
        # Retrieves token from user role in database if it hasn't expires else create a new one
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    
    def revoke_token(self):
        # Allowing users to revoke tokens
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        
    
    @staticmethod
    def check_token(token):
        # Function to check if token has expired
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
    
    
    def to_dict(self):
        # Pieces information to a Python dictionary
        data = {
                "id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "accounts": url_for('api.get_accounts', id=self.id),
                "transactions":url_for('api.get_user_transactions', id=self.id)
        }
        return data
    
    
    def from_dict(self, data, new_user=False, update_email=False, change_password=False):
        # Converts parsed JSON to a Python dictionary
        if new_user and 'password' in data:
            for field in ['first_name', 'last_name', 'email']:
                if field in data:
                    setattr(self, field, data[field])
            self.set_password(data["password"])
        elif update_email and 'new_email' in data:
            setattr(self, "email", data["new_email"])
        elif change_password and 'new_password' in data:
            self.set_password(data["new_password"])
            

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)


class TransactionType(db.Model):
    """Transaction Type SQlite ORM model
        Columns:
            - id (SQLite int): primary key
            - name (SQLite str64): transaction type in system (e.g. Deposit, Withdrawal, Transfer, Other)
        
    """
    __tablename__ = "transaction_type_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    txn = db.relationship('Transactions', backref='transaction_type') # Adds txn attribute to Transactions model
    
    def __init__(self, **kwargs):
        super(TransactionType, self).__init__(**kwargs)
    
    @staticmethod
    def insert_transaction_types()->None:
        # Static method to push roles into database.
        transaction_types = {'Deposit', 'Withdrawal', 'Transfer', 'New Account', 'Other'}
        for type in transaction_types:
            transaction_type = TransactionType.query.filter_by(name=type).first()
            if transaction_type is None:
                transaction_type = TransactionType(name=type)
            db.session.add(transaction_type)
        db.session.commit()
        
    def __repr__(self):
        return '<Transaction Types %r>' % self.name


class Transactions(db.Model):
    """Transactions SQlite ORM model

    Columns:
        - id (SQLite int): primary key
        - receiver (SQLite int): account number of receiver
        - sender (SQLite int): account number of sender
        - amount (SQLite int): amount involved in the transaction
        - date_time (SQLite DateTime): date time of the transaction
        - transaction_type_id (SQLite int): id corresponding to the transaction types (e.g. Deposits, Transfer)
    
    """
    
    __tablename__ = "transactions_table"
    
    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.Integer, db.ForeignKey("accounts_table.account_num"), nullable=False)
    sender = db.Column(db.Integer, db.ForeignKey("accounts_table.account_num"), nullable=False)
    amount = db.Column(db.Integer)
    date_time = db.Column(db.DateTime, index=True)
    transaction_type_id = db.Column(db.Integer, db.ForeignKey('transaction_type_table.id'))
    
    def to_dict(self):
        # Pieces transaction information to a Python dictionary
        data = {
                "id": self.id,
                "from": self.sender_account.account_owner.first_name + " " + self.sender_account.account_owner.last_name,
                "from_acc": self.sender,
                "to": self.receiver_account.account_owner.first_name + " " + self.receiver_account.account_owner.last_name,
                "to_acc": self.receiver,
                "amount": self.amount,
                "type": self.transaction_type.name
        }
        return data
    
    @staticmethod
    def to_collection_dict(user):
        # Pieces all transactions involving user into a Python dictionary
        # Added the possibility to query for multiple accounts
        account = Accounts.query.filter_by(account_owner=user).all()
        txns = []
        for acc in account:
            transactions = Transactions.query.filter((Transactions.receiver_account == acc) | 
                                                 (Transactions.sender_account == acc)).order_by(Transactions.date_time.desc()).all()
            for txn in transactions:
                txns.append(txn.to_dict())
        
        data = {
            "transactions": txns,
            "_meta": {
                'total_transactions':len(txns)
            }
        }
        return data
    
    
    
    def __repr__(self):
        return '< {} Txn {}: {} - {}, amount {}, type: {}>'.format(self.date_time, self.id, self.sender, self.receiver, self.amount, self.transaction_type_id)


class Accounts(db.Model):
    """Bank account SQlite ORM model

    Columns:
        account_num (SQLite int): bank account number
        owner (SQLite int): bank account owner, mapped to users_table id
        balance (SQLite int): account balance, default 0 during account creation
    """
    
    __tablename__ = "accounts_table"
    
    account_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('users_table.id'))
    balance = db.Column(db.Float, default=0.00)
    receiver_acc = db.relationship("Transactions", foreign_keys="Transactions.receiver", backref="receiver_account", lazy="dynamic")
    sender_acc = db.relationship("Transactions", foreign_keys="Transactions.sender", backref="sender_account", lazy="dynamic")
    
    def new_account(self):
        """
        Sets balance of fresh account to 0
        """
        if not self.balance:
            self.balance = 0
    
    def update_balance(self, amount):
        """Updates Account balance

        Args:
            amount (int): update amount. Negative for fund removal.
        """
        self.balance += amount
    
    
    def to_dict(self):
        # Pieces account information to a Python dictionary
        data = {
                "account_num": self.account_num,
                "owner": self.owner,
                "balance": self.balance
        }
        return data
    
    @staticmethod
    def to_collection_dict(user):
        # Pieces all accounts belonging to user into a Python dictionary
        total = 0
        accounts = Accounts.query.filter_by(account_owner=user).all()
        for item in accounts:
            total += item.balance
        data = {
            "accounts": [item.to_dict() for item in accounts],
            "_meta": {
                'num_accounts':len(accounts),
                'total_balance': total
            }
        }
        return data
    
    
    def __repr__(self):
        return '<Account no. {}, owner {}: {}>'.format(self.owner, self.account_num, self.balance)