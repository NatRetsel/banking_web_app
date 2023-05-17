# Banking web app
## A basic personal banking web app

A personal banking web app supporting user creation, login and showing recent transactions and account balance. Backend written in Flask and SQLite database with Alembic migration support. Frontend written in html and Flask bootstrap. A detailed walkthrough can be found in my medium articles:

- [part one](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-1-8fcc69b80ab2)
- [part two](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-2-e11ebb4d1703)

### Folder Contents
- app 
  - templates (html files for the different routes in route.py)
    - base.html
    - index.html
    - login.html
    - register.html
  - __init__.py 
  - forms.py (FlaskForm objects for user registration and login)
  - models.py (database tables as classes)
  - routes.py (URLs of webapp)
- migrations (Alembic database migration folder)
- webapp.py (app initializer script)
- config.py (configuration settings)
- .flaskenv
- data.sqlite
- requirements.txt

### To run: 
- pip install -r requirements.txt in virtual environment
- Change configuration settings in app/__init__.py:
  - Development: 'development'
  - Testing: 'testing'
  - Production: 'production'
  - Default: Development
- flask run

### SQLite Database
- Tables
  - Roles (one to many relation to User table)
    - id (primary key)
    - role
  - User 
    - id (primary key)
    - first name
    - last name
    - email
    - password hash
    - role_id (foreign key to Roles table)
    - balance
    - txns (foreign key to Transactions table)
  - Transactions
    - id (primary key)
    - txn_to (receiver)
    - txn_from (sender)
    - date

- Initialize role id accordingly:
  - 'Admin', id 1
  - 'Moderator', id 2
  - 'User', id 3


## Roadmap

#### 1.) User login creation, local database storage with SQLite
  - User registration (done)
  - User login (done)
  - User data (done):
    - Email
    - Password hash
    - First name
    - Last name
  - Relational data (TBD):
    - Roles (admin, user etc) (Done) 
    - Transactions (WIP relating foreign key to User table)
  
#### 2.) Unit testing for part 1 (WIP)
  - Setup
  - teardown 
  - if app exist
  - if configuration == config['testing']
  - default role id is "user" upon new registration

#### 3.) Refactor with application factory and blueprint

#### 4.) Email support with Flask-Mail

#### 5.) User Transaction details

