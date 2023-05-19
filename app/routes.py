from flask import render_template, redirect, url_for, flash, session, request, Response
from flask_login import current_user, login_user, logout_user
from app.forms import RegistrationForm, LoginForm
from app.models import User, Role
from app import app, db
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
def index() -> Response:
    first_name = session.get('first_name')
    return render_template('index.html', first_name=first_name)

@app.route('/register', methods=['GET', 'POST'])
def register() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_role = Role.query.filter_by(name='User').first()
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, role_id=user_role.id) # Defaults role to user role 
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please login')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout() -> Response:
    logout_user()
    return redirect(url_for('index'))