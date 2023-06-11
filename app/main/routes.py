from flask import render_template, session, Response 
from flask_login import current_user
from app.models import Accounts, User, Transactions
from app import db
from . import main

@main.route('/')
@main.route('/index')
def index() -> Response:
    """Index / Home route for the app. 
    If user is logged in:
        - queries for
            -user's first name
            -user's account
            -user's transaction
    
    Returns:
        Response: index.html
    """
    balance = None
    first_name = session.get('first_name')
    transactions = []
    account = None
    if current_user.is_authenticated:
        user = User.query.filter_by(email=current_user.email).first()
        account = Accounts.query.filter_by(owner=user.id).first()
        balance = account.balance
        transactions = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).all()
    return render_template('index.html', first_name=first_name, balance=balance, account=account, transactions=transactions)