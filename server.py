from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_utils import chat_completion_request
from file_manager import delete_file, rename_file, rename_subdir, list_files, read_file, write_file, create_project, create_subdir, delete_subdir
from web_scraper import browse_web
from ast import literal_eval

app = Flask(__name__)
CORS(app)

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
        "description": "List the files and subdirectories in a specified project directory",
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
        "name": "delete_file",
        "description": "Delete a specified file in a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to delete",
                },
            },
            "required": ["project_name", "filename"],
        },
    },
    {
        "name": "rename_file",
        "description": "Rename a specified file in a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "old_filename": {
                    "type": "string",
                    "description": "The existing name of the file",
                },
                "new_filename": {
                    "type": "string",
                    "description": "The new name of the file",
                },
            },
            "required": ["project_name", "old_filename", "new_filename"],
        },
    },
    {
        "name": "create_subdir",
        "description": "Create a new subdirectory in a specified project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "dirname": {
                    "type": "string",
                    "description": "The name of the subdirectory to create",
                },
            },
            "required": ["project_name", "dirname"],
        },
    },
    {
        "name": "delete_subdir",
        "description": "Delete a specified subdirectory in a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "dirname": {
                    "type": "string",
                    "description": "The name of the subdirectory to delete",
                },
            },
            "required": ["project_name", "dirname"],
        },
    },
    {
        "name": "rename_subdir",
        "description": "Rename a specified subdirectory in a project",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project",
                },
                "old_dirname": {
                    "type": "string",
                    "description": "The existing name of the subdirectory",
                },
                "new_dirname": {
                    "type": "string",
                    "description": "The new name of the subdirectory",
                },
            },
            "required": ["project_name", "old_dirname", "new_dirname"],
        },
    }
]

# Mapping function names to function objects
FUNCTION_MAP = {
    'create_project': create_project,
    'create_subdir': create_subdir,
    'delete_subdir': delete_subdir,
    'rename_subdir': rename_subdir,
    'list_files': list_files,
    'delete_file': delete_file,
    'read_file': read_file,
    'write_file': write_file,
    'rename_file': rename_file,
    'browse_web': browse_web
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if 'messages' not in data:
        return jsonify({'error': 'Missing messages parameter'}), 400
    messages = data['messages']

    if 'model' not in data:
        return jsonify({'error': 'Missing model parameter'}), 400
    model = data['model']

    while True:
        response = chat_completion_request(messages=messages, model=model, functions=functions)
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
    app.run(debug=True, use_reloader=False)
