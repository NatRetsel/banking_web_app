from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, DecimalField, IntegerField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    """User registration form 
        - User account registration. Login ID will be the email address
        - Inherits FlaskForm object
        - Fields:
            - first_name (str): User first name
            - last_name (str): User last name
            - email (str): User email
            - password (str): User password
            - password (str): User password repeat
            - submit ('POST')

    Raises:
        ValidationError: when an email is already present in the database
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email',validators=[DataRequired(), Email()] )
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')
    
    def validate_email(self, email: str) -> None:
        user: Optional[str] = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    """User login form
        - User account registration. Login ID will be the email address
        - Inherits FlaskForm object
        - Fields:
            - email (str): User email
            - password (str): User password
            - remember_me (bool): Fed into flask-login's user_login function dealing with session management
            - submit ('POST')

    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TransferForm(FlaskForm):
    """Transfer funds form
        - User fund transfer. Login is required to access the form
        - User inputs recipient account number and desired transfer amount
    
    """
    recipient_acc_num = IntegerField('To Account', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Send')
    

class DepositForm(FlaskForm):
    """User Deposit funds form
        - For the purposes of this application, this form mimics cash deposits 
        - User inputs the amount after logging in, to which the amount is added to the balance
        - A deposit transaction is also added

    """
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Send')
    