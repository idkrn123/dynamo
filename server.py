import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_utils import chat_completion_request
from github_manager import *
from web_scraper import browse_web
from ast import literal_eval

app = Flask(__name__)
CORS(app)

with open('available_functions.json') as json_file:
    available_functions = json.load(json_file)

FUNCTION_MAP = {}
for function in available_functions:
    FUNCTION_MAP[function['name']] = globals()[function['name']]
    # debug because i'm upset
    print(f"Loaded function {function['name']}")


@app.route('/chat', methods=['POST'])
def chat():
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
    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)