import os
import json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ast import literal_eval
from .chat_utils import chat_completion_request
from .github_manager import *
from .web_scraper import browse_web
from .models import User, ApiKey, db
from .auth import auth
from .billing import charge_user

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.register_blueprint(auth, url_prefix='/auth')
db.init_app(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.before_first_request
def create_tables():
    db.create_all()

dir_path = os.path.dirname(os.path.realpath(__file__))
json_file_path = os.path.join(dir_path, 'available_functions.json')

with open(json_file_path) as json_file:
    available_functions = json.load(json_file)

FUNCTION_MAP = {}
for function in available_functions:
    FUNCTION_MAP[function['name']] = globals()[function['name']]
    print(f"Loaded function {function['name']}")

@app.route('/chat', methods=['POST'])
def chat():
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 400
    key = ApiKey.query.filter_by(key=api_key).first()
    if not key:
        return jsonify({'error': 'Invalid API key'}), 401

    data = request.get_json()
    if 'messages' not in data:
        return jsonify({'error': 'Missing messages parameter'}), 400
    messages = data['messages']

    if 'model' not in data:
        return jsonify({'error': 'Missing model parameter'}), 400
    model = data['model']

    functions = []
    if 'functions' in data:
        available_functions_dict = {func['name']: func for func in available_functions}

        for function_obj in data['functions']:
            function_name = function_obj['name']
            if function_name not in available_functions_dict:
                return jsonify({'error': f'Function {function_name} not found'}), 404
            functions.append(available_functions_dict[function_name])

    while True:
        if functions:
            response = chat_completion_request(messages=messages, model=model, functions=functions)
        else:
            response = chat_completion_request(messages=messages, model=model)
        response_json = response.json()
        try:
            assistant_message = response_json['choices'][0]['message']
        except KeyError as e:
            print(response.text)
            if response_json['error']:
                error = response_json['error']['message']
            else:
                error = "unknown"
            return jsonify({'openai-server-error': f'Error: {error}'}), 500

        if assistant_message.get('function_call'):
            function_name = assistant_message['function_call']['name']
            function_arguments = assistant_message['function_call']['arguments']
            function = FUNCTION_MAP.get(function_name)

            if not function:
                return jsonify({'error': f'Function {function_name} not found'}), 404
            arguments = literal_eval(function_arguments)
            result = function(**arguments)
            messages.append({'role': 'function', 'name': function_name, 'content': result})
        else:
            messages.append(assistant_message)
            break

        if not charge_user(key.user_id, 0.01):
        return jsonify({'error': 'Insufficient balance'}), 402
        
    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
