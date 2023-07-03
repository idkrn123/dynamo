from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_utils import chat_completion_request
from github_manager import *
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
        "description": "List the files in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "branch": {
                    "type": "string",
                    "description": "The name of the branch",
                    "default": "main",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to read",
                },
                "branch": {
                    "type": "string",
                    "description": "The name of the branch",
                    "default": "main",
                },
            },
            "required": ["repo_name", "filename"],
        },
    },
    {
        "name": "write_file",
        "description": "Write the contents to a file in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
                "branch": {
                    "type": "string",
                    "description": "The name of the branch",
                    "default": "main",
                },
            },
            "required": ["repo_name", "filename", "content"],
        },
    },
    {
        "name": "create_repo",
        "description": "Create a new repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository to create",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a specified file in a repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the file to delete",
                },
                "branch": {
                    "type": "string",
                    "description": "The name of the branch",
                    "default": "main",
                },
            },
            "required": ["repo_name", "filename"],
        },
    },
    {
        "name": "rename_file",
        "description": "Rename a specified file in a repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "old_filename": {
                    "type": "string",
                    "description": "The existing name of the file",
                },
                "new_filename": {
                    "type": "string",
                    "description": "The new name of the file",
                },
                "branch": {
                    "type": "string",
                    "description": "The name of the branch",
                    "default": "main",
                },
            },
            "required": ["repo_name", "old_filename", "new_filename"],
        },
    },
    {
        "name": "delete_repo",
        "description": "Delete a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "list_branches",
        "description": "List the branches in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "get_branch",
        "description": "Get a specific branch in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "branch_name": {
                    "type": "string",
                    "description": "The name of the branch",
                },
            },
            "required": ["repo_name", "branch_name"],
        },
    },
    {
        "name": "create_branch",
        "description": "Create a new branch in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "branch_name": {
                    "type": "string",
                    "description": "The name of the branch",
                },
                "base_branch_name": {
                    "type": "string",
                    "description": "The name of the branch to branch from",
                    "default": "main",
                },
            },
            "required": ["repo_name", "branch_name"],
        },
    },
    {
        "name": "create_pull_request",
        "description": "Create a new pull request in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "title": {
                    "type": "string",
                    "description": "The title of the pull request",
                },
                "body": {
                    "type": "string",
                    "description": "The body of the pull request",
                },
                "head": {
                    "type": "string",
                    "description": "The name of the branch where your changes are implemented",
                },
                "base": {
                    "type": "string",
                    "description": "The name of the branch you want the changes pulled into",
                },
            },
            "required": ["repo_name", "title", "body", "head", "base"],
        },
    },
    {
        "name": "list_pull_requests",
        "description": "List the pull requests in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "get_pull_request",
        "description": "Get a specific pull request in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "pull_request_number": {
                    "type": "integer",
                    "description": "The number of the pull request",
                },
            },
            "required": ["repo_name", "pull_request_number"],
        },
    },
    {
        "name": "merge_pull_request",
        "description": "Merge a specific pull request in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "pull_request_number": {
                    "type": "integer",
                    "description": "The number of the pull request",
                },
                "commit_message": {
                    "type": "string",
                    "description": "The message of the commit",
                },
            },
            "required": ["repo_name", "pull_request_number"],
        },
    },
    {
        "name": "list_commits",
        "description": "List the commits in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                    "default": "main",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "get_commit",
        "description": "Get a specific commit in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                },
                "commit_sha": {
                    "type": "string",
                    "description": "The SHA of the commit",
                },
            },
            "required": ["repo_name", "commit_sha"],
        },
    },
    {
        "name": "list_open_issues",
        "description": "List the open issues in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
            },
            "required": ["repo_name"],
        },
    },
    {
        "name": "get_issue",
        "description": "Get a specific issue in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "issue_number": {
                    "type": "integer",
                    "description": "The number of the issue",
                },
            },
            "required": ["repo_name", "issue_number"],
        },
    },
    {
        "name": "create_issue_comment",
        "description": "Create a comment on a specific issue in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "issue_number": {
                    "type": "integer",
                    "description": "The number of the issue",
                },
                "comment": {
                    "type": "string",
                    "description": "The comment to add to the issue",
                },
            },
            "required": ["repo_name", "issue_number", "comment"],
        },
    },
    {
        "name": "close_issue",
        "description": "Close a specific issue in a specified repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "issue_number": {
                    "type": "integer",
                    "description": "The number of the issue",
                },
            },
            "required": ["repo_name", "issue_number"],
        },
    },
]

# Mapping function names to function objects
FUNCTION_MAP = {f.__name__: f for f in [create_repo, delete_repo, list_files, delete_file, read_file, write_file, rename_file, 
                                        list_branches, get_branch, create_branch, create_pull_request, list_open_issues, get_issue, 
                                        create_issue_comment, close_issue, browse_web, list_pull_requests, get_pull_request, merge_pull_request]}

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