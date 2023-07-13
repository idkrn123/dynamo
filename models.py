from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy import DateTime, func
from werkzeug.exceptions import BadRequest
import os
import requests

load_dotenv()
db = SQLAlchemy()

SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_ENV = os.getenv('FLASK_ENV')

class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    apikeys = db.relationship('ApiKey', backref='user', lazy=True)
    openai_api_key = db.Column(EncryptedType(db.String, SECRET_KEY, AesEngine, 'pkcs5'))
    github_oauth_token = db.Column(EncryptedType(db.String, SECRET_KEY, AesEngine, 'pkcs5'))
    openai_api_key_updated_at = db.Column(DateTime(timezone=True), default=func.now())
    github_oauth_token_updated_at = db.Column(DateTime(timezone=True), default=func.now())
    balance = db.Column(db.Integer, default=0)  # Store balance in cents

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    @staticmethod
    def validate_username(username):
        if not username:
            raise BadRequest('Missing username')
        if User.query.filter_by(username=username).first():
            raise BadRequest('Username already exists')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_password_format(password):
        # Add your password format validation logic here
        pass

    def generate_auth_token(self, expiration=600):
        """Generate an authentication token."""
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def check_recaptcha(data):
        """Verify the recaptcha response."""
        if 'recaptcha_response' not in data and FLASK_ENV != 'development':
            raise BadRequest('Missing recaptcha response')
        recaptcha_response = data['recaptcha_response'] if FLASK_ENV != 'development' else 'test'
        recaptcha_secret = 'your_recaptcha_secret_key'  # replace with your secret key from https://www.google.com/recaptcha/admin
        recaptcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response_json = requests.post(
            recaptcha_verify_url,
            data={
                'secret': recaptcha_secret,
                'response': recaptcha_response
            }
        ).json() if FLASK_ENV != 'development' else {'success': True}
        result = response_json
        if not result['success']:
            raise BadRequest('Invalid recaptcha')
        
class ApiKey(db.Model):
    """API key model."""

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        self.key = self.generate_key()

    @staticmethod
    def generate_key():
        """Generate a key."""
        return generate_password_hash(os.urandom(32).hex())