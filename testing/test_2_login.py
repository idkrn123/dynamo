import requests
import json
import os

def test_login():
    url = "http://localhost:5000/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {'username': 'testuser', 'password': 'testpassword'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert 'token' in response.json()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(dir_path, 'token.txt')

    with open(token_file_path, 'w') as file:
        file.write(response.json()['token'])
