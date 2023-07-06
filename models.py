from dotenv import load_dotenv
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy import DateTime, func
import os

load_dotenv()
db = SQLAlchemy()

print(os.getenv('SECRET_KEY'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    apikeys = db.relationship('ApiKey', backref='user', lazy=True)
    openai_api_key = db.Column(EncryptedType(db.String, os.getenv('SECRET_KEY'), AesEngine, 'pkcs5'))
    github_oauth_token = db.Column(EncryptedType(db.String, os.getenv('SECRET_KEY'), AesEngine, 'pkcs5'))
    openai_api_key_updated_at = db.Column(DateTime(timezone=True), default=func.now())
    github_oauth_token_updated_at = db.Column(DateTime(timezone=True), default=func.now())
    balance = db.Column(db.Float, default=0.0)

    def generate_auth_token(self, expiration=600):
        s = Serializer(os.getenv('SECRET_KEY'), expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            if 'Bearer ' in token:
                token = token.split('Bearer ')[1]
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        self.key = generate_password_hash(os.urandom(32))