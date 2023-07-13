from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, InternalServerError
from ..models import User, db
from .auth import UserNotFound

class InsufficientBalance(BadRequest):
    def __init__(self, current_balance, required_balance):
        self.current_balance = current_balance
        self.required_balance = required_balance
        super().__init__(f"Insufficient balance. Current: {self.current_balance}, Required: {self.required_balance}")

def charge_user(user_id, amount):
    try:
        user = User.query.with_for_update().get(user_id)
        if round(float(user.balance), 2) < round(float(amount), 2):
            raise InsufficientBalance(round(float(user.balance), 2), round(float(amount), 2))
        user.balance -= amount
        db.session.commit()
    except NoResultFound:
        raise UserNotFound('User not found')
    except Exception as e:
        db.session.rollback()
        raise InternalServerError('Database error: {}'.format(e))

def add_money(user_id, amount):
    try:
        user = User.query.with_for_update().get(user_id)
        user.balance += amount
        db.session.commit()
    except NoResultFound:
        raise UserNotFound('User not found')
    except Exception as e:
        db.session.rollback()
        raise InternalServerError('Database error: {}'.format(e))

def get_balance(user_id):
    try:
        user = User.query.get(user_id)
        return user.balance
    except NoResultFound:
        raise UserNotFound('User not found')
    except Exception as e:
        raise InternalServerError('Error getting balance: {}'.format(e))