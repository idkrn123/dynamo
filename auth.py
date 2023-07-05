from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
from datetime import datetime
from .models import User, ApiKey, db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 200

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return make_response('Could not verify', 401)
    token = user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@auth.route('/apikeys', methods=['GET', 'POST', 'DELETE'])
def apikeys():
    if request.method == 'GET':
        user = User.verify_auth_token(request.headers.get('Authorization'))
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        apikeys = [{'id': key.id, 'key': key.key[-4:]} for key in user.apikeys]
        return jsonify({'apikeys': apikeys})
    elif request.method == 'POST':
        user = User.verify_auth_token(request.headers.get('Authorization'))
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        new_key = ApiKey(user_id=user.id)
        db.session.add(new_key)
        db.session.commit()
        return jsonify({'message': 'API key generated', 'key': new_key.key})
    elif request.method == 'DELETE':
        user = User.verify_auth_token(request.headers.get('Authorization'))
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        key = ApiKey.query.get(request.get_json()['id'])
        if key and key.user_id == user.id:
            db.session.delete(key)
            db.session.commit()
            return jsonify({'message': 'API key deleted'})
        else:
            return jsonify({'message': 'API key not found'}), 404

@auth.route('/keys', methods=['POST'])
def store_keys():
    data = request.get_json()
    if not data or ('openai_api_key' not in data and 'github_oauth_token' not in data):
        return jsonify({'message': 'Missing keys in request'}), 400
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    if 'openai_api_key' in data:
        user.openai_api_key = data['openai_api_key']
        user.openai_api_key_updated_at = datetime.utcnow()
    if 'github_oauth_token' in data:
        user.github_oauth_token = data['github_oauth_token']
        user.github_oauth_token_updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Keys updated successfully'})

@auth.route('/keys', methods=['GET'])
def get_keys():
    user = User.verify_auth_token(request.headers.get('Authorization'))
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    return jsonify({
        'openai_api_key': bool(user.openai_api_key),
        'openai_api_key_updated_at': user.openai_api_key_updated_at.timestamp() if user.openai_api_key else None,
        'github_oauth_token': bool(user.github_oauth_token),
        'github_oauth_token_updated_at': user.github_oauth_token_updated_at.timestamp() if user.github_oauth_token else None
    })
