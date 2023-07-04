from app.api import api
from flask import jsonify, request, url_for, abort
from app.models import User, Accounts, Transactions, TransactionType
from datetime import datetime
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth


@api.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    """Get a user by ID

    Args:
        id (int): ID of user

    Returns:
        JSON: A JSON object containing the informaiton about the user
        404: When user does not exist
        403: When token authentication fails
    
    Example:
        >>> get_user(1)
        {
            "id":1,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@email.com",
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
    """
    if token_auth.current_user().id != id:
        abort(403)
    return jsonify(User.query.get_or_404(id).to_dict())


@api.route('/users/<int:user_id>/transactions/<int:txn_id>', methods=['GET'])
@token_auth.login_required
def get_user_transaction(user_id, txn_id):
    """Get a transaction involving the user by transaction ID and user ID.
        - Peforms token authentication check
        - Queries for valid user else return 404
        - Queries for transaction with ID matching txn_id
        - Returns JSON object of transaction only if user is in the sender or receving end of the transaction
        
    Args:
        user_id (int): ID of the user
        txn_id (int): ID of the transaction

    Returns:
        JSON: A JSON object of the transaction with ID of txn_id which involves the user with ID of user_id.
        400: When transaction does not involve user with ID user_id.
        404: When User of ID user_id or transaction of ID txn_id does not exist.
        403: When token authentication fails
    
    Example:
        >>> get_user_transaction(1,2)
        {
            "id": 2,
            "amount": 5,
            "from": "Jane Doe",
            "from_acc": 1,
            "to": "John Doe",
            "to_acc": 2,
            "type": "Transfer"
        }
    
    
    """
    if token_auth.current_user().id != user_id:
        abort(403)
    user = User.query.get_or_404(user_id)
    txn = Transactions.query.get_or_404(txn_id)
    if txn.receiver_account.account_owner == user or txn.sender_account.account_owner == user:
        return jsonify(txn.to_dict())
    return bad_request("Invalid credentials")


@api.route('/users/<int:id>/transactions', methods=['GET'])
@token_auth.login_required
def get_user_transactions(id):
    """Get transactions involving the user by user ID.
    NOTE: Improvement by adding pagination in the event of numerous transaction history

    Args:
        id (int): ID of user

    Returns:
        JSON: A JSON object containing ALL transactions involving user with ID == id
        404: Invalid user
        403: When token authentication fails
    
    Example:
        >>> get_user_transactions(1)
        {
            "_meta": {
                "total_transactions":3
            },
            "transactions": [
                {
                    "amount": 5
                    "from": "John Doe" 
                    "from_acc": 2,
                    "id": 3,
                    "to": "Jane Doe",
                    "to_acc": 1,
                    "type": "Transfer"
                },
                {
                    "amount": 10
                    "from": "Jane Doe" 
                    "from_acc": 1,
                    "id": 2,
                    "to": "Jane Doe",
                    "to_acc": 1,
                    "type": "Deposit"
                },
                {
                    "amount": 0
                    "from": "Jane Doe" 
                    "from_acc": 1,
                    "id": 1,
                    "to": "Jane Doe",
                    "to_acc": 1,
                    "type": "New Account"
                }
                
            ]
        }
    """
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    return jsonify(Transactions.to_collection_dict(user))
    


@api.route('/users', methods=['POST'])
def create_account():
    """Creates new user account and bank account with the supplied information in JSON from request
        - Checks if keyword fields are present and if the email is available for taking
        JSON keyword fields:
            'first_name': first name of user
            'last_name': last name of user
            'email': email address of user, used for login 
            'password': password for user account
    Returns:
        response 200 (JSON): JSON representation of the newly created user account
        400: keyword fields not present or email address has been taken
    
    Example:
        >>> create_account() first_name="Jane" last_name="Doe" email="janedoe@email.com" password=<password>
        {
            "id":1,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@email.com",
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
        
    
    """
    data = request.get_json() or {}
    if 'first_name' not in data or 'last_name' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include first name, last name, email and password fields')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    
    # Add user
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    
    # Add account
    user_acc = Accounts(account_owner=user)
    db.session.add(user_acc)
    db.session.commit()
    
    # Add txn
    txn_type = TransactionType.query.filter_by(name="New Account").first()
    txn = Transactions(receiver_account=user_acc, sender_account=user_acc, amount=0, date_time=datetime.utcnow(), 
                        transaction_type=txn_type)
    
    db.session.add(txn)
    db.session.commit()
    
    
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@api.route('/users/<int:id>/change_email', methods=['PUT'])
@token_auth.login_required
def update_user_email(id):
    """Updates user email address by user ID with the supplied information in JSON from request
        - First does token authentication
        - Checks for valid user with id
        - Checks for required keyword fields and if new email is free for taking
        - JSON keyword fields:
            "new_email": new email address of user to change to

    Args:
        id (int): ID of user

    Returns:
        response 200 (JSON): JSON representation of user of ID = id
        404: Invalid user
        403: Token authentication fails
        400: Email has been taken
    
    Example:
        >>> update_user_email(1) new_email=janedoe2@email.com
        {
            "id":1,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe2@email.com",
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
        
        
    """
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'new_email' in data and data['new_email'] != user.email and User.query.filter_by(email=data['new_email']).first():
        return bad_request('Please use a different email')
    user.from_dict(data, new_user=False, update_email=True, change_password=False)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 200
    return response


@api.route('users/<int:id>/change_password', methods=['PUT'])
@token_auth.login_required
def update_password(id):
    """Updates user email address by user ID with the supplied information in JSON from request
        - First does token authentication
        - Checks for valid user with id
        - Checks for required keyword fields and if old_password matches user's current password
        - JSON keyword fields:
            "old_password": user's current password
            "new_password": user's new password

    Args:
        id (int): ID of user

    Returns:
        response 200 (JSON): JSON representation of user
        404: Invalid user
        403: Token authentication fails
        400: current password does not match, changing to the same password as current password, keyword fields missing
    
    Example:
        >>> update_password(1) old_password=<old_password> new_password=<new_password>
        {
            "id":1,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe2@email.com",
            "accounts": "/api/users/1/accounts",
            "transactions":"/api/users/1/transactions"
        }
    """
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'old_password' in data and 'new_password' in data and data['old_password'] == data['new_password']:
        return bad_request('Your password cannot be the same as your old password')
    if 'old_password' in data and 'new_password' in data and not user.check_password(data['old_password']):
        return bad_request('Invalid credentials')
    if 'old_password' in data and 'new_password' in data and user.check_password(data['old_password']):
        user.from_dict(data, new_user=False, update_email=False, change_password=True)
        db.session.commit()
        response = jsonify(user.to_dict())
        response.status_code=200
        return response
    return bad_request('Please make sure to have the valid fields')
        


@api.route('users/<int:id>/accounts', methods=['GET'])
@token_auth.login_required
def get_accounts(id):
    """Get collection of accounts belonging to user by ID
        - NOTE: Scope of current project assumes 1 account per user, this route is developed in light of possible future features 
        to allow multiple bank accounts per user.
    Args:
        id (int): ID of user

    Returns:
        JSON: JSON representation of a collection of user accounts
        404: Invalid user
        403: Token authentication fails
    
    Example:
        >>> get_accounts(1)
        {
            "_meta": {
                "num_accounts": 1,
                "total_balance": 11.0
            },
            
            "accounts": [
                {
                    "account_num":1,
                    "balance": 11.0,
                    "owner": 1
                }
            ]
        }
    """
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    return jsonify(Accounts.to_collection_dict(user))


@api.route('users/<int:user_id>/accounts/<int:account_id>', methods=['GET'])
@token_auth.login_required
def get_user_account(user_id, account_id):
    """Get a account by id of account_id (account number) belonging to user by id of user_id.
        - Performs token authentication
        - Queries for valid user and account
        - Verifies that account belongs to user before sending a JSON response

    Args:
        user_id (int): ID of user
        account_id (int): ID of user account (account number)

    Returns:
        JSON: JSON representation of user account
        403: Token authentication fails
        404: Invalid user or account. When account does not belong to user
        400: Invalid credentials
    
    Example:
        >>> get_user_account(1,1)
        {
            "account_num": 1,
            "balance": 11.0,
            "owner": 1
        }
    """
    if token_auth.current_user().id != user_id:
        abort(403)
    user = User.query.get_or_404(user_id)
    account = Accounts.query.get_or_404(account_id)
    if account.account_owner == user:
        return jsonify(account.to_dict())
    return bad_request('Invalid credentials')


@api.route('users/<int:user_id>/accounts/<int:account_num>/deposit', methods=['POST'])
@token_auth.login_required
def deposit(user_id, account_num):
    """Mimicks cash deposits to user account with id of account_num belonging to user with id of user_id. Amount to deposit
    supplied in JSON object during request.
        - Token authentication
        - Checks for valid user, account and makes sure that account belongs to user
        - Checks for valid deposit_amount field in request JSON
        - Updates account balance, creates a deposit transaction and updates database
        
        JSON keyword fields
            - 'deposit_amount': amount to be deposited into account
    

    Args:
        user_id (id): ID of user
        account_num (id): ID of account

    Returns:
        response 201 (JSON): JSON representation of the user account and deposit transaction
        403: Token authentication fails
        404: Invalid user or account
        400: Invalid credentials. When trying to deposit into account not belonging to owner or a invalid deposit amount is supplied
        
    Example:
        >>> deposit(1,1) deposit_amount=10
        {
            "account": {
                "account_num": 1,
                "balance": 11.0,
                "owner": 1
            },
            "transaction": {
                "amount": 11
                "from": "Jane Doe" 
                "from_acc": 1,
                "id": 2,
                "to": "Jane Doe",
                "to_acc": 1,
                "type": "Deposit"
            }
        }
        
    """
    if token_auth.current_user().id != user_id:
        abort(403)
    user = User.query.get_or_404(user_id)
    account = Accounts.query.get_or_404(account_num)
    data = request.get_json() or {}
    if account.account_owner == user:
        if "deposit_amount" in data and float(data["deposit_amount"]) > 0:
            account.update_balance(float(data["deposit_amount"]))
            
            txn_type = TransactionType.query.filter_by(name="Deposit").first()
            txn = Transactions(receiver_account=account, sender_account=account, amount=float(data["deposit_amount"]), date_time=datetime.utcnow(), transaction_type=txn_type)
            
            db.session.add_all([account, txn])
            db.session.commit()
            
            response = jsonify({'account': account.to_dict(), 'transaction': txn.to_dict()})
            response.status_code=201
            return response
        return bad_request('Please enter a valid deposit amount')
    return bad_request('Invalid credentials')


@api.route('users/<int:user_id>/accounts/<int:account_num>/transfer', methods=['POST'])
@token_auth.login_required
def transfer(user_id, account_num):
    """Fund transfers from user account to a specified registered user account. 
    Details of destination account and transfer amount are supplied in the JSON request.
        - Token authentication
        - Query for valid sender user, account and sender account indeed belongs to user
        - Checks for required receiver information in the JSON request
        - Checks that amount is valid, not greater than amount held in sender's account
        - Updates balance in both accounts
        - Creates "Transfer" type transaction
        
        JSON keyword fields
        - "to_account_num": recipient account number
        - "amount": amount to be transferred

    Args:
        user_id (int): ID of user performing the fund transfer
        account_num (int): ID of user account where funds are moved from

    Returns:
        response 201 (JSON): JSON representation of sender account and transfer transaction details
        403: Token authentication fails
        404: Invalid user or accounts
        400: Invalid credentials, attempt to transfer from an account not belonging to user, invalid transfer amount
    
    Example:
        >>> transfer(1,1) to_account_num=2 amount=5
        {
            "account": {
                "account_num": 1,
                "balance": 11.0,
                "owner": 1
            },
            "transaction": {
                "amount": 5
                "from": "Jane Doe" 
                "from_acc": 1,
                "id": 3,
                "to": "John Doe",
                "to_acc": 5,
                "type": "Transfer"
            }
        }
    """
    if token_auth.current_user().id != user_id:
        abort(403)
    user = User.query.get_or_404(user_id)
    account = Accounts.query.get_or_404(account_num)
    data = request.get_json() or {}
    if account.account_owner == user:
        if "to_account_num" in data and data["to_account_num"] != account.account_num:
            recipient_account = Accounts.query.get_or_404(data["to_account_num"])
            if "amount" in data and float(data["amount"]) >0 and account.balance - float(data["amount"]) >= 0:
                account.update_balance(-float(data["amount"]))
                recipient_account.update_balance(float(data["amount"]))
                
                txn_type = TransactionType.query.filter_by(name="Transfer").first()
                txn = Transactions(receiver_account=recipient_account, sender_account=account, amount=float(data["amount"]), date_time=datetime.utcnow(), transaction_type=txn_type)
                db.session.add_all([recipient_account, account, txn])
                db.session.commit()
                
                response = jsonify({'account': account.to_dict(), 'transaction': txn.to_dict()})
                response.status_code = 201
                return response
            return bad_request('Please enter a valid transfer amount')
    return bad_request('Invalid credentials')

