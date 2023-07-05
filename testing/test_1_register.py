import requests
import json

def test_register():
    url = "http://localhost:5000/auth/register"
    headers = {'Content-Type': 'application/json'}
    data = {'username': 'testuser', 'password': 'testpassword'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert response.json()['message'] == 'Registered successfully'
