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
    return jsonify(User.query.get_or_404(id).to_dict())


@api.route('/users/<int:user_id>/transactions/<int:txn_id>', methods=['GET'])
@token_auth.login_required
def get_user_transaction(user_id, txn_id):
    user = User.query.get_or_404(user_id)
    account = Accounts.query.filter_by(owner=user.id).first()
    txn = Transactions.query.filter((Transactions.receiver_account == account) | 
                                                 (Transactions.sender_account == account)).order_by(Transactions.date_time.desc()).all()
    for transaction in txn:
        if transaction.id == txn_id:
            return jsonify(Transactions.query.get_or_404(txn_id).to_dict())
    return bad_request("Invalid credentials")


@api.route('/users/<int:id>/transactions', methods=['GET'])
@token_auth.login_required
def get_user_transactions(id):
    user = User.query.get_or_404(id)
    return jsonify(Transactions.to_collection_dict(user))
    


@api.route('/users', methods=['POST'])
def create_account():
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
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'new_email' in data and data['new_email'] != user.email and User.query.filter_by(email=data['new_email']).first():
        return bad_request('Please use a different email')
    user.from_dict(data, new_user=False, update_email=True, change_password=False)
    db.session.commit()
    return jsonify(user.to_dict())


@api.route('users/<int:id>/change_password', methods=['PUT'])
@token_auth.login_required
def update_password(id):
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
        return jsonify(user.to_dict())
    return bad_request('Please make sure to have the valid fields')
        


@api.route('users/<int:id>/accounts', methods=['GET'])
@token_auth.login_required
def get_accounts(id):
    user = User.query.get_or_404(id)
    return jsonify(Accounts.to_collection_dict(user))


@api.route('users/<int:user_id>/accounts/<int:account_id>', methods=['GET'])
@token_auth.login_required
def get_user_account(user_id, account_id):
    user = User.query.get_or_404(user_id)
    account = Accounts.query.get_or_404(account_id)
    if account.account_owner == user:
        return jsonify(account.to_dict())
    return bad_request('Invalid credentials')
