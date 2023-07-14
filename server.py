import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from ast import literal_eval
from .openai_handler import chat_completion_request, APIKeyError, HTTPError
from .functions.github_functions import GithubManager
from .functions.web_functions import browse_web
from .models import User, ApiKey, db
from .routes.auth import auth
from .routes.billing import charge_user

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.register_blueprint(auth, url_prefix='/auth')
db.init_app(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

with app.app_context():
    db.create_all()
    jwt = JWTManager(app)

def load_functions():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    json_file_path = os.path.join(dir_path, 'available_functions.json')

    with open(json_file_path) as json_file:
        available_functions = json.load(json_file)

    function_map = {}
    for function in available_functions:
        try:
            function_map[function['name']] = globals()[function['name']]
            print(f"Loaded function {function['name']}")
        except KeyError:
            if hasattr(GithubManager, function['name']):
                function_map[function['name']] = function['name']
                print(f"Loaded GitHub function {function['name']}")
            else:
                print(f"Function {function['name']} not found in server.py or any managers")
    return function_map, available_functions

FUNCTION_MAP, AVAILABLE_FUNCTIONS = load_functions()

def get_user(api_key):
    if api_key:
        api_key_obj = ApiKey.query.filter_by(key=api_key).first()
        if api_key_obj:
            return api_key_obj.user
    else:
        verify_jwt_in_request()
        user_identity = get_jwt_identity()
        if user_identity:
            return User.query.filter_by(username=user_identity).first()
        else:
            raise ValueError("API key or user token must be provided.")

@app.route('/chat', methods=['POST'])
def chat():
    api_key = request.headers.get('X-API-KEY')
    try:
        user = get_user(api_key)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    data = request.get_json()
    messages = data.get('messages')
    model = data.get('model')
    if not messages or not model:
        return jsonify({'error': 'Missing messages or model parameter'}), 400

    functions = []
    if 'functions' in data:
        available_functions_dict = {func['name']: func for func in AVAILABLE_FUNCTIONS}
        for function_obj in data['functions']:
            function_name = function_obj['name']
            if function_name not in available_functions_dict:
                return jsonify({'error': f'Function {function_name} not found'}), 404
            functions.append(available_functions_dict[function_name])
            if os.getenv('FLASK_ENV') == 'development':
                print(str(functions))

    openai_api_key = user.openai_api_key or None
    github_oauth_token = user.github_oauth_token or None
    github_manager = GithubManager(github_oauth_token)

    while True:
        try:
            response_object = chat_completion_request(messages=messages, model=model, functions=functions, openai_api_key=openai_api_key)
        except (APIKeyError, HTTPError, Exception) as e:
            return jsonify({'error': str(e)}), 500

        assistant_message = response_object.get('choices', [{}])[0].get('message')
        if not assistant_message:
            error = response_object.get('error', {}).get('message', 'unknown')
            return jsonify({'openai-server-error': f'Error: {error}'}), 500

        if assistant_message.get('function_call'):
            function_name = assistant_message['function_call']['name']
            function_arguments = literal_eval(assistant_message['function_call']['arguments'])

            if hasattr(github_manager, function_name):
                if github_oauth_token is None:
                    return jsonify({'error': 'User has no GitHub OAuth token'}), 401
                function = getattr(github_manager, function_name)
            elif function_name in FUNCTION_MAP:
                function = FUNCTION_MAP[function_name]
            else:
                return jsonify({'error': f'Function {function_name} not found'}), 404

            result = function(**function_arguments)
            messages.append({'role': 'function', 'name': function_name, 'content': result})
        else:
            messages.append(assistant_message)
            break

        # we'll do this later and add stripe or something. open an issue if you want this faster i guess
        # price = 0.01 * (len(messages) - 1)
        # charge_user(user.id, price)

    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)