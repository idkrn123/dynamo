import os
import json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ast import literal_eval
from .openai_handler import chat_completion_request, APIKeyError, HTTPError
from .functions.github_functions import GithubManager
from .functions.web_functions import browse_web
from .models import User, ApiKey, db
from .routes.auth import auth
from .routes.billing import billing

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(billing, url_prefix='/billing')
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
    try:
        FUNCTION_MAP[function['name']] = globals()[function['name']]
        print(f"Loaded function {function['name']}")
    except KeyError:
        if hasattr(GithubManager, function['name']):
            FUNCTION_MAP[function['name']] = function['name']
            print(f"Loaded GitHub function {function['name']}")
        else:
            print(f"Function {function['name']} not found in server.py or any managers")
    

@app.route('/chat', methods=['POST'])
def chat():
    api_key = request.headers.get('X-API-KEY')
    if not api_key and 'Authorization' not in request.headers:
        return jsonify({'error': "API key or user token must be provided."}), 400

    if api_key:
        api_key_user = User.query.filter_by(apikeys=api_key).first()
        if 'Authorization' in request.headers:
            token_user = User.verify_auth_token(request.headers.get('Authorization'))
            if api_key_user != token_user:
                return jsonify({'error': 'API key and token were both provided and users do not match...?'}), 418 # dude you broke it so badly it became a teapot
        user = api_key_user
    else:
        if 'Authorization' not in request.headers:
            return jsonify({'error': "API key or user token must be provided."}), 400
        try:
            token_user = User.verify_auth_token(request.headers.get('Authorization'))
        except:
            return jsonify({'error': "Invalid token"}), 401
        user = token_user

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

    if not user:
        if api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        else:
            if 'Authorization' not in request.headers:
                return jsonify({'error': "No auth data provided"}), 401
            else:
                return jsonify({'error': "Invalid token"}), 401
    # get api key from database
    if user.openai_api_key:
        openai_api_key = user.openai_api_key
    else:
        return jsonify({'error': 'User has no OpenAI API key'}), 401
    
    # we make github oauth token optional
    if user.github_oauth_token:
        github_oauth_token = user.github_oauth_token
    else:
        github_oauth_token = None

    github_manager = GithubManager(github_oauth_token)

    while True:
        try:
            if functions:
                response = chat_completion_request(messages=messages, model=model, functions=functions, openai_api_key=openai_api_key)
            else:
                response = chat_completion_request(messages=messages, model=model, openai_api_key=openai_api_key)
        except APIKeyError as e:
            return jsonify({'error': str(e)}), 401
        except HTTPError as e:
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
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

            if hasattr(github_manager, function_name):
                function = getattr(github_manager, function_name)
            elif function_name in FUNCTION_MAP:
                function = FUNCTION_MAP[function_name]
            else:
                return jsonify({'error': f'Function {function_name} not found'}), 404

            arguments = literal_eval(function_arguments)
            result = function(**arguments)
            messages.append({'role': 'function', 'name': function_name, 'content': result})
        else:
            messages.append(assistant_message)
            break

        price = 0.01 * (len(messages) - 1)
        if not billing.charge_user(user, price):
            return jsonify({'error': 'Insufficient balance'}), 402
        
    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
