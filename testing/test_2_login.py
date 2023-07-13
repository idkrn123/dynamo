import requests
import json
import os

username_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'username.txt')
password_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'password.txt')

with open(username_file_path) as file:
    username = file.read()

with open(password_file_path) as file:
    password = file.read()

def test_login():
    url = "http://localhost:5000/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {'username': username, 'password': password}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())
    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(dir_path, 'token.txt')

    with open(token_file_path, 'w') as file:
        file.write(response.json()['token'])
        
    assert response.status_code == 200
    assert 'token' in response.json()
