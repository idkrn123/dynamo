import re
import requests
import dotenv
import os
from flask import Blueprint, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from ..models import User, ApiKey, db

dotenv.load_dotenv()
auth = Blueprint('auth', __name__)

def verify_recaptcha(response_token):
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'secret': secret_key,
        'response': response_token
    }
    response = requests.post(url, data=data)
    return response.json().get('success', False)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, 'Missing username or password')
    if ('recaptcha' not in data) or (not verify_recaptcha(data['recaptcha'])):
        if not os.getenv('FLASK_ENV') == 'development':
            abort(400, 'Invalid reCAPTCHA')
        else:
            print('Invalid reCAPTCHA excepted due to development environment')
    if not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
        abort(400, 'Username must only contain letters, numbers and underscores')
    if len(data['username']) < 3 or len(data['username']) > 20:
        abort(400, 'Username must be between 3 and 20 characters')
    if len(data['password']) < 8 or len(data['password']) > 1000:
        abort(400, 'Password must be over 8 characters long')
    if User.query.filter_by(username=data['username']).first():
        abort(400, 'Username already taken')
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))
    return jsonify({'message': 'Registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if ('recaptcha' not in data) or (not verify_recaptcha(data['recaptcha'])):
        if not os.getenv('FLASK_ENV') == 'development':
            abort(400, 'Invalid reCAPTCHA')
        else:
            print('Invalid reCAPTCHA excepted due to development environment')
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        abort(401, 'Could not verify')
    try:
        token = user.generate_auth_token()
    except Exception as e:
        abort(500, 'Token generation error: {}'.format(e))
    return jsonify({'token': token.decode('ascii')}), 200

@auth.route('/apikeys', methods=['GET', 'POST', 'DELETE'])
def apikeys():
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        abort(401, 'Invalid token')
    try:
        if request.method == 'GET':
            apikeys = [{'id': key.id, 'key': key.key[-4:]} for key in user.apikeys]
            return jsonify({'apikeys': apikeys})
        elif request.method == 'POST':
            new_key = ApiKey(user_id=user.id)
            db.session.add(new_key)
            db.session.commit()
            return jsonify({'message': 'API key generated', 'key': new_key.key})
        elif request.method == 'DELETE':
            key = ApiKey.query.get(request.get_json()['id'])
            if key and key.user_id == user.id:
                db.session.delete(key)
                db.session.commit()
                return jsonify({'message': 'API key deleted'})
            else:
                abort(404, 'API key not found')
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))

@auth.route('/keys', methods=['POST'])
def store_keys():
    data = request.get_json()
    if not data or ('openai_api_key' not in data and 'github_oauth_token' not in data):
        abort(400, 'Missing keys in request')
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        abort(401, 'Invalid token')
    try:
        if 'openai_api_key' in data:
            if not re.match(r'^sk-', data['openai_api_key']):
                user.openai_api_key_updated_at = datetime.utcnow()
            else:
                user.openai_api_key = data['openai_api_key']
                user.openai_api_key_updated_at = datetime.utcnow()
        if 'github_oauth_token' in data:
            if not re.match(r'^[a-z0-9]+$', data['github_oauth_token']):
                user.github_oauth_token_updated_at = datetime.utcnow()
            else:
                user.github_oauth_token = data['github_oauth_token']
                user.github_oauth_token_updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Keys updated successfully'})
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))

@auth.route('/keys', methods=['GET'])
def get_keys():
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        abort(401, 'Invalid token')
    try:
        return jsonify({
            'openai_api_key': bool(user.openai_api_key),
            'openai_api_key_updated_at': user.openai_api_key_updated_at.timestamp() if user.openai_api_key else None,
            'github_oauth_token': bool(user.github_oauth_token),
            'github_oauth_token_updated_at': user.github_oauth_token_updated_at.timestamp() if user.github_oauth_token else None
        })
    except Exception as e:
        abort(500, 'Database error: {}'.format(e))