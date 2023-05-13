from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    
    __tablename__ = "roles_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    
    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    
    __tablename__ = "users_table"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles_table.id'))
    balance = db.Column(db.BigInteger)
    txns = db.Column(db.BigInteger, db.ForeignKey('transactions_table.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

class Transactions(db.Model):
    
    __tablename__ = "transactions_table"
    
    id = db.Column(db.BigInteger, primary_key=True)
    txn_to = db.Column(db.String(64), index=True)
    txn_from = db.Column(db.String(64), index=True)
    amount = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Txn {}: {} - {}, {}>'.format(self.id, self.txn_to, self.txn_from, self.amount)