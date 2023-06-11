# Banking web app

A personal banking web app supporting user creation, login and showing recent transactions and account balance. Backend written in Flask and SQLite database with Alembic migration support. Frontend written in html and Flask bootstrap. A detailed walkthrough can be found in my medium articles:

* [Part one: <u>Basic app and web forms</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-1-8fcc69b80ab2)

* [Part two: <u>Database relation and migration</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-2-e11ebb4d1703)

* [Part three: <u>User registration and login</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-3-f116e6fa881b)

* [Part four: <u>Application factory and blueprint</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-4-e9e66769f293) 

* [Part five: <u>Unit and Functional tests</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-4-e9e66769f293)

* [Part six: <u>Transactions</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-6-ca3d14473c59)

### Features
Users are able to register an account, deposit funds and transfer to existing accounts in the database. Users can view their account details and transactions in the index page.
![Register page](/screenshots/register.png "Register page")
![Login page](/screenshots/login.png "Login page")
![Index page](/screenshots/index_logged_in.png "Index page")

### To run: 
- pip install -r requirements.txt in virtual environment
- Change configuration settings in app/__init__.py:
  - Development: 'development'
  - Testing: 'testing'
  - Production: 'production'
  - Default: Development
- In the command line: flask run

### SQLite Database
![Database relational figure](/screenshots/Untitled%20(7).png "Database relational figure")
