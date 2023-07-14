import requests
import json
import os

def test_apikeys_generate():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(dir_path, 'token.txt')
    with open(token_file_path, 'r') as file:
        token = file.read()
    url = "http://localhost:5000/auth/apikeys"
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers)
    assert response.status_code == 200
    assert 'key' in response.json()

    apikey_file_path = os.path.join(dir_path, 'apikey.txt')
    with open(apikey_file_path, 'w') as file:
        file.write(response.json()['key'])