import requests
import json
import os

def test_keys_post():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(dir_path, 'token.txt')

    with open(token_file_path, 'r') as file:
        token = file.read()
    url = "http://localhost:5000/auth/keys"
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = {'openai_api_key': 'sk-afakeopenaikey', 'github_oauth_token': 'github_pat_afakegithubkey'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert response.json()['message'] == 'Keys updated successfully'