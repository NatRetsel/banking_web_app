# Banking web app

My attempt at learning web development by repurposing [Miguel Grinberg's Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) into a personal banking web app supporting user creation, login and showing recent transactions and account balance. Backend written in Flask and SQLite database with Alembic migration support. Frontend written in html and Flask bootstrap. A detailed walkthrough can be found in my medium articles:

* [Part one: <u>Basic app and web forms</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-1-8fcc69b80ab2)

* [Part two: <u>Database relation and migration</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-2-e11ebb4d1703)

* [Part three: <u>User registration and login</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-3-f116e6fa881b)

* [Part four: <u>Application factory and blueprint</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-4-e9e66769f293) 

* [Part five: <u>Unit and Functional tests</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-4-e9e66769f293)

* [Part six: <u>Transactions</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-6-ca3d14473c59)

* [Part seven: <u>Updating User Information</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-7-92edd149fc35)

* [Part eight: <u>REST API</u>](https://medium.com/@sunsethorizonstories/banking-web-app-stories-part-8-fa886a921434)

### Features
Users are able to register a user account together with a bank account, deposit funds and transfer to existing bank accounts in the database. Users can view their bank account details and transactions in the index page.

Note: 
* For the scope of this project, we assumed one bank account per user account. However, some APIs are configured for the scenario where each user can have multiple bank accounts. This leaves an option for added features in the future.
* This project also assumes that users can and will only transaction between users of the same bank. A possible feature in the future would be to include which bank the user's account is registered under in the Accounts table to mimic and keep track of inter-bank transactions.

#### Registration
![Register page](/screenshots/register.png "Register page")
#### Login
![Login page](/screenshots/login.png "Login page")
#### Logged in index page
![Index page](/screenshots/index_logged_in_v2.png "Index page")

### To run: 
- pip install -r requirements.txt in virtual environment
- Change configuration settings in app/__init__.py:
  - Development: 'development'
  - Testing: 'testing'
  - Production: 'production'
  - Default: Development
- In the command line: flask run

### SQLite Database
![Database relational figure](/screenshots/banking_web_app_db_diagram.png "Database relational figure")

### REST API endpoints
![REST API endpoints](/screenshots/rest_routes.png "Table containing REST API endpoints")
