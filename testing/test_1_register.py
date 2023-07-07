import requests
import os
import json
import random

random_username = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(10))
random_password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(10))

dir_path = os.path.dirname(os.path.realpath(__file__))
username_file_path = os.path.join(dir_path, 'username.txt')
password_file_path = os.path.join(dir_path, 'password.txt')

with open(username_file_path, 'w') as file:
    file.write(random_username)

with open(password_file_path, 'w') as file:
    file.write(random_password)

def test_register():
    url = "http://localhost:5000/auth/register"
    headers = {'Content-Type': 'application/json'}
    data = {'username': random_username, 'password': random_password}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(str(response.json))
    assert response.status_code == 201
    assert response.json()['message'] == 'Registered successfully'
