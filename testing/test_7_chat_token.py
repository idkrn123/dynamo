import requests
import json
import os

def test_chat_token():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(dir_path, 'token.txt')
    with open(token_file_path, 'r') as file:
        token = file.read()
    url = "http://localhost:5000/chat"
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    data = {'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}], 'model': 'gpt3'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.json()['error'] == 'User has no OpenAI API key'