from flask import Flask, request, jsonify
from chat_utils import chat_completion_request
from file_manager import FUNCTION_MAP
from web_scraper import browse_web
from ast import literal_eval

app = Flask(__name__)

functions = [
    {
        "name": "browse_web",
        "description": "Browse the web and return the content of a webpage",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to browse",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_files",
        "description": "List the files in a specified project directory",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project directory",
                },
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file in a specified project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to read",
                },
            },
            "required": ["project_name", "filename"],
        },
    },
    {
        "name": "write_file",
        "description": "Write the contents to a file in a specified project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": ["project_name", "filename", "content"],
        },
    },
    {
        "name": "create_project",
        "description": "Create a new project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project to create",
                },
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "list_projects",
        "description": "List all projects",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if 'messages' not in data:
        return jsonify({'error': 'Missing messages parameter'}), 400
    messages = data['messages']

    while True:
        response = chat_completion_request(messages, functions=functions)
        response_json = response.json()
        assistant_message = response_json['choices'][0]['message']

        if assistant_message.get('function_call'):
            function_name = assistant_message['function_call']['name']
            function_arguments = assistant_message['function_call']['arguments']
            function = FUNCTION_MAP[function_name] if function_name in FUNCTION_MAP else None

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
    app.run(debug=True)
