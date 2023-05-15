from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    """Role SQlite ORM model
        Columns:
            - id (SQLite int): primary key
            - name (SQLite str64): role name in system (e.g. Admin, Moderator, User)
        
    """
    __tablename__ = "roles_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role') # Adds role attribute to User model
    
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
            - balance (SQLite bigint): user account balance
            - txns (SQLite bigint): transactions id involving user, mapped to Transactions table

    """
    
    __tablename__ = "users_table"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles_table.id'))
    balance = db.Column(db.BigInteger)
    txns = db.Column(db.BigInteger, db.ForeignKey('transactions_table.id'))
    
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

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

class Transactions(db.Model):
    """Transactions SQlite ORM model

    Columns:
        - id (SQLite bigint): primary key
        - txn_to (SQLite str64): first name + last name of receiver (may / may not exist in local bank database)
        - txn_from (SQLite str64): first name + last name of sender (may / may not exist in local bank database)
        - amount (SQLite bigint): amount involved in the transaction

    
    """
    
    __tablename__ = "transactions_table"
    
    id = db.Column(db.BigInteger, primary_key=True)
    txn_to = db.Column(db.String(64), index=True)
    txn_from = db.Column(db.String(64), index=True)
    amount = db.Column(db.BigInteger)
    
    def __repr__(self):
        return '<Txn {}: {} - {}, {}>'.format(self.id, self.txn_to, self.txn_from, self.amount)