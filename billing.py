from .models import User, db

def charge_user(user_id, amount):
    user = User.query.get(user_id)
    if user.balance < amount:
        return False
    user.balance -= amount
    db.session.commit()
    return True
