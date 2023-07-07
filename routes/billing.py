from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from ..models import User, db

def charge_user(user_id, amount):
    user = User.query.get(user_id)
    if not user:
        abort(404, 'User not found')
    if user.balance < amount:
        abort(400, 'Insufficient balance')
    try:
        user.balance -= amount
        db.session.commit()
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))
    return True

def add_money(user_id, amount):
    user = User.query.get(user_id)
    if not user:
        abort(404, 'User not found')
    try:
        user.balance += amount
        db.session.commit()
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))
    return True

def get_balance(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, 'User not found')
    return user.balance

billing = Blueprint('billing', __name__)

@billing.route('/balance', methods=['GET'])
@login_required
def balance():
    try:
        return jsonify({'balance': get_balance(current_user.id)})
    except Exception as e:
        abort(500, 'Error getting balance: {}'.format(e))