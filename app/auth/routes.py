from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from ..main.forms import RegistrationForm, LoginForm, TransferForm, DepositForm
from app.models import User, Role, Accounts, Transactions, TransactionType
from datetime import datetime
from .. import db
from . import auth
from werkzeug.urls import url_parse


@auth.route('/register', methods=['GET', 'POST'])
def register() -> Response:
    """User registration route
    1.) If user is logged in, redirects to index page
    2.) Upon validating registration form, stores user password hash, creates a User model and pushes into database. Then redirects to login
    3.) If form validation fails, redirects back to register page.

    Returns:
        Response: login page if registration is successful else register page. If user is logged in then redirects to index.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data) # Defaults role to user role 
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        
        user_acc = Accounts(account_owner=user)
        db.session.add(user_acc)
        db.session.commit()
        
        txn_type = TransactionType.query.filter_by(name="New Account").first()
        txn = Transactions(receiver_account=user_acc, sender_account=user_acc, amount=0, date_time=datetime.utcnow(), 
                           transaction_type=txn_type)
        
        db.session.add(txn)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    """User login route
    1.) If user is already logged in, redirects to index route
    2.) If login form is validated:
        (i) if user exists and password matches
            - redirects to previous viewed page if it exists else index page
        (ii) if user does not exist or password is wrong
            - flask error message and redirects to login page

    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
@login_required
def logout() -> Response:
    """User log out route
    Logs user out using logout_user() function in Flask-Login extension
    Returns:
        Response: index page
    """
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/transfer',  methods=['GET', 'POST'])
@login_required
def transfer() -> Response:
    """Sending money from own balance to other accounts in the same database

    Returns:
        Response: index page
    """
    form = TransferForm()
    if form.validate_on_submit():
        recipient_acc = Accounts.query.filter_by(account_num=form.recipient_acc_num.data).first()
        # recipient_acc_num = recipient_acc.account_num
        sender_acc = Accounts.query.filter_by(owner=current_user.id).first()
        # sender_acc_num = sender_acc.account_num
        if recipient_acc is None:
            flash('User not found', 'danger')
            return redirect(url_for('auth.transfer'))
        elif sender_acc.balance < form.amount.data:
            flash('Insufficient account balance', 'danger')
            return redirect(url_for('auth.transfer'))
        else:
            recipient_acc.update_balance(form.amount.data)
            sender_acc.update_balance(-form.amount.data)
            
            txn_type = TransactionType.query.filter_by(name="Transfer").first()
            txn = Transactions(receiver_account=recipient_acc, sender_account=sender_acc, amount=form.amount.data, date_time=datetime.utcnow(), transaction_type=txn_type)
            db.session.add_all([recipient_acc, sender_acc, txn])
            db.session.commit()
            flash('Transfer Success!', 'success')
            return redirect(url_for('main.index'))
    return render_template('auth/transfer.html', title='Funds Transfer', form=form)


@auth.route('/deposit',  methods=['GET', 'POST'])
@login_required
def deposit() -> Response:
    """Deposit function mimicking cash deposit feature
        - Upon form validation, adds amount into user account balance, creates a corresponding transaction
        and pushes into database
    Returns:
        Response: main.index.html if successful else auth/deposit.html
    """
    form = DepositForm()
    if form.validate_on_submit():
        acc_owner = User.query.filter_by(email=current_user.email).first()
        own_account = Accounts.query.filter_by(owner=acc_owner.id).first()
        own_account.update_balance(form.amount.data)
        
        txn_type = TransactionType.query.filter_by(name="Deposit").first()
        txn = Transactions(receiver_account=own_account, sender_account=own_account, amount=form.amount.data, date_time=datetime.utcnow(), transaction_type=txn_type)
        db.session.add_all([own_account, txn])
        
        db.session.commit()
        flash('Deposit Success!', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/deposit.html', title='Deposit', form=form)
        