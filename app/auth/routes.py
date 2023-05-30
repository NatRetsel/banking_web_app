from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user
from ..main.forms import RegistrationForm, LoginForm
from app.models import User, Role
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

    Returns:
        Response: _description_
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout() -> Response:
    """User log out route
    Logs user out using logout_user() function in Flask-Login extension
    Returns:
        Response: index page
    """
    logout_user()
    return redirect(url_for('main.index'))