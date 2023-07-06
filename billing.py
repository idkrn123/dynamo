from .models import User, db

# let's add a function to charge a user's account so we can make money $$$
def charge_user(user_id, amount):
    user = User.query.get(user_id)
    if user.balance < amount:
        return False
    user.balance -= amount
    db.session.commit()
    return True

# let's also add a function to add money to a user's account so we can give them money $$$
def add_money(user_id, amount):
    user = User.query.get(user_id)
    user.balance += amount
    db.session.commit()
    return True

# let's also add a function to get a user's balance, will be useful for the frontend
def get_balance(user_id):
    user = User.query.get(user_id)
    return user.balance

# in fact, let's make a flask blueprint for checking a user's balance so we can use it in the frontend
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

billing = Blueprint('billing', __name__)

@billing.route('/balance', methods=['GET'])
@login_required
def balance():
    return jsonify({'balance': get_balance(current_user.id)})