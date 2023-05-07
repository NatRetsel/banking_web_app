from flask import render_template
from app import app
#Contains the different URLs of the bank webapp

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'John'}
    account_balance = 1
    transactions = [
        {
            'id': "001",
            'Date': "01/01/2023",
            'To': "Jane",
            'From': "John",
            'Amount': 2
        },
        {
            'id': "002",
            'Date': "02/01/2023",
            'To': "John",
            'From': "Jane",
            'Amount': 1
        }
    ]
    return render_template('index.html', title='Home', user=user, transactions=transactions)