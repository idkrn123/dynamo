import re
import requests
import dotenv
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from datetime import datetime
from logging import getLogger
from ..models import User, ApiKey, db

dotenv.load_dotenv()
auth = Blueprint('auth', __name__)

logger = getLogger(__name__)

class UserNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def abort_on_exception(e, message):
    logger.error(f'Error: {e}')
    raise InternalServerError(f'{message}: {e}')

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        raise BadRequest('Missing username or password')
    User.check_recaptcha(data)
    User.validate_username(username=data['username'])
    User.validate_password_format(data['password'])
    new_user = User(username=data['username'], password=data['password'])
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        abort_on_exception(e, 'Database error')
    return jsonify({'message': 'Registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    User.check_recaptcha(data)
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        raise Unauthorized('Could not verify')
    try:
        access_token = create_access_token(identity=data['username'])
    except Exception as e:
        abort_on_exception(e, 'Token generation error')
    return jsonify({'token': access_token}), 200


@auth.route('/apikeys', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def apikeys():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        raise Unauthorized('Invalid token')
    try:
        if request.method == 'GET':
            apikeys = [{'id': key.id, 'key': key.key[-4:]} for key in user.apikeys]
            return jsonify({'apikeys': apikeys})
        elif request.method == 'POST':
            new_key = ApiKey(user_id=user.id)
            db.session.add(new_key)
            db.session.commit()
            print(new_key.key)
            return jsonify({'message': 'API key generated', 'key': new_key.key})
        elif request.method == 'DELETE':
            key = ApiKey.query.get(request.get_json()['id'])
            if key and key.user_id == user.id:
                db.session.delete(key)
                db.session.commit()
                return jsonify({'message': 'API key deleted'})
            else:
                raise BadRequest('API key not found')
    except Exception as e:
        abort_on_exception(e, 'Database error')

@auth.route('/keys', methods=['POST'])
@jwt_required()
def store_keys():
    data = request.get_json()
    if not data or ('openai_api_key' not in data and 'github_oauth_token' not in data):
        raise BadRequest('Missing keys in request')
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        raise Unauthorized('Invalid token')
    try:
        if 'openai_api_key' in data and data['openai_api_key']:
            if not re.match(r'^sk-', data['openai_api_key']):
                return jsonify({'message': 'Invalid OpenAI API key'}), 400
            else:
                user.openai_api_key = data['openai_api_key']
                user.openai_api_key_updated_at = datetime.utcnow()
        if 'github_oauth_token' in data and data['github_oauth_token']:
            if not re.match(r'^github_pat_', data['github_oauth_token']):
                return jsonify({'message': 'Invalid GitHub OAuth token'}), 400
            else:
                user.github_oauth_token = data['github_oauth_token']
                user.github_oauth_token_updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Keys updated successfully'})
    except Exception as e:
        abort_on_exception(e, 'Database error')

@auth.route('/keys', methods=['GET'])
@jwt_required()
def get_keys():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        raise Unauthorized('Invalid token')
    try:
        return jsonify({
            'openai_api_key': bool(user.openai_api_key),
            'openai_api_key_updated_at': user.openai_api_key_updated_at.timestamp() if user.openai_api_key else None,
            'github_oauth_token': bool(user.github_oauth_token),
            'github_oauth_token_updated_at': user.github_oauth_token_updated_at.timestamp() if user.github_oauth_token else None
        })
    except Exception as e:
        abort_on_exception(e, 'Database error')

@auth.route('/change_username', methods=['POST'])
@jwt_required()
def change_username():
    data = request.get_json()
    if not data or 'new_username' not in data or 'password' not in data:
        raise BadRequest('Missing new username or password')
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        raise Unauthorized('Invalid token')
    if not user.check_password(data['password']):
        raise Unauthorized('Password verification failed')
    User.validate_username(username=data['new_username'])
    try:
        user.username = data['new_username']
        db.session.commit()
        return jsonify({'message': 'Username changed successfully'}), 200
    except Exception as e:
        abort_on_exception(e, 'Database error')

@auth.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    if not data or 'current_password' not in data or 'new_password' not in data:
        raise BadRequest('Missing current or new password')
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        raise Unauthorized('Invalid token')
    if not user.check_password(data['current_password']):
        raise Unauthorized('Password verification failed')
    User.validate_password_format(data['new_password'])
    try:
        user.password = User.hash_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        abort_on_exception(e, 'Database error')

@auth.route('/delete_account', methods=['POST'])
@jwt_required()
def delete_account():
    data = request.get_json()
    if not data or 'password' not in data:
        raise BadRequest('Missing password')
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        raise Unauthorized('Invalid token')
    if not user.check_password(data['password']):
        raise Unauthorized('Password verification failed')
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        abort_on_exception(e, 'Database error')