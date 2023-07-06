let usernameInput = document.getElementById('username-input');
let passwordInput = document.getElementById('password-input');
let loginForm = document.getElementById('login-form');
let loginLink = document.getElementById('login-button');
let loginShow = document.getElementById('login-show-button');
let keysLink = document.getElementById('keys-button');
let loginModal = document.getElementById('login-modal');
let keysPanel = document.getElementById('keys-panel');
let apiKey = '';

window.onload = function () {
    apiKey = localStorage.getItem('apiKey');
    if (apiKey) {
        loginLink.style.display = 'none';
        keysLink.style.display = 'block';
        loginModal.style.display = 'none';
        keysPanel.style.display = 'none';
        loginForm.style.display = 'none';
        chatForm.style.display = 'block';
        chatContext.push({
            "role": "assistant",
            "content": "Hello! How can I assist you today?"
        });
        printMessage('assistant-message', 'Hello! How can I assist you today?');
    } else {
        loginLink.style.display = 'block';
        keysLink.style.display = 'none';
        loginModal.style.display = 'block'; // Display the login modal when there's no API key
        loginForm.style.display = 'block'; // Display the login form when there's no API key
        chatForm.style.display = 'none';
    }
    document.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
    });
};

loginLink.onclick = function(event) {
    event.preventDefault();
    loginModal.style.display = "block";
    loginForm.style.display = "block"; // Always display the login form when the login modal is shown
}

keysLink.onclick = function(event) {
    event.preventDefault();
    keysPanel.style.display = "block";
}

document.getElementById('login-close').onclick = function() {
    loginModal.style.display = "none";
}

document.getElementById('keys-close').onclick = function() {
    keysPanel.style.display = "none";
}

async function login() {
    const response = await fetch("http://localhost:5000/auth/login", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "username": usernameInput.value, "password": passwordInput.value })
    });

    const data = await response.json();
    if (data.token) {
        localStorage.setItem('token', data.token);
        loginModal.style.display = 'none';
        chatForm.style.display = 'block';
        getApiKey();
    } else {
        alert('Login failed');
    }
}

async function getApiKey() {
    const token = localStorage.getItem('token');
    const response = await fetch("http://localhost:5000/auth/apikeys", {
        method: 'POST',
        headers: {
            "Authorization": token
        }
    });

    let usertoken = '';
    usertoken = localStorage.getItem('token');

    const data = await response.json();
    if (data.key) {
        apiKey = data.key;
        localStorage.setItem('apiKey', apiKey);
    } else if (data.message === 'Invalid token') {
        loginModal.style.display = 'block'; // Display the login modal when the token is invalid
        loginForm.style.display = 'block'; // Display the login form when the token is invalid
        document.getElementById('login-button').style.display = 'block'; // Ensure that the login button is displayed
    }
}

async function storeKeys() {
    const token = localStorage.getItem('token');
    const response = await fetch("http://localhost:5000/auth/keys", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ "openai_api_key": openaiKeyInput.value, "github_oauth_token": githubTokenInput.value })
    });

    let usertoken = '';
    usertoken = localStorage.getItem('token');

    const data = await response.json();
    if (data.message === 'Keys updated successfully') {
        alert('Keys stored successfully');
    } else if (data.message === 'Invalid token') {
        loginModal.style.display = 'block'; // Display the login modal when the token is invalid
        loginForm.style.display = 'block'; // Display the login form when the token is invalid
        document.getElementById('login-button').style.display = 'block'; // Ensure that the login button is displayed
    } else {
        alert('Failed to store keys');
    }
}

async function deleteKeys() {
    const token = localStorage.getItem('token');
    const response = await fetch("http://localhost:5000/auth/keys", {
        method: 'DELETE',
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();
    if (data.message === 'Keys deleted successfully') {
        alert('Keys deleted successfully');
    } else {
        alert('Failed to delete keys');
    }
}

document.getElementById('login-button').onclick = login; // Assign the login function to the onclick event of the login button