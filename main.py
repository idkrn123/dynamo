import argparse
import os
import requests
from chat_utils import chat_completion_request, pretty_print_conversation
from file_manager import FUNCTION_MAP
from jsonpath_ng import parse
from web_scraper import browse_web

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run the chatbot with optional debug mode.")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

# Ensure the "projects" directory exists
if not os.path.exists("projects"):
    os.makedirs("projects")

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

messages = [
    {"role": "system", "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo. You can create Python projects, generate multiple files according to Python standards, and populate them with content to form programs of various natures. You can also manage projects and files using the provided functions. When writing code, add a touch of humor in the comments to make the code more enjoyable to read. Never shorten code output when writing files."},
]

while True:
    print("User (type 'END' on a new line to finish input):")
    user_input = ""
    while True:
        line = input()
        if line == "END":
            break
        user_input += line + "\n"
    messages.append({"role": "user", "content": user_input.strip()})
    while True:
        response = chat_completion_request(messages, functions=functions)
        if args.debug:
            print(f"Debug: Response: {response.text}")
        try:
            response_json = response.json()
            assistant_message = parse('$.choices[0].message').find(response_json)
            if not assistant_message:
                assistant_message = {"role": "assistant", "content": "Sorry, I encountered an error while processing your request."}
            else:
                assistant_message = assistant_message[0].value
        except Exception as e:
            print(f"Error processing assistant's response: {e}")
            assistant_message = {"role": "assistant", "content": "Sorry, I encountered an error while processing your request."}
        messages.append(assistant_message)

        if assistant_message.get("function_call"):
            function_name = assistant_message["function_call"]["name"]
            function_arguments = assistant_message["function_call"]["arguments"]
            function = FUNCTION_MAP[function_name]
            try:
                arguments = eval(function_arguments)
            except Exception as e:
                print(f'Error parsing function arguments: {e}')
                break
            try:
                result = function(**arguments)
                messages.append({"role": "function", "name": function_name, "content": result})
            except Exception as e:
                print(f'Error calling function {function_name}: {e}')
        else:
            break
    pretty_print_conversation(messages)
