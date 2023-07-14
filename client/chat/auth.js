let usernameInput = document.getElementById('username-input');
let passwordInput = document.getElementById('password-input');
let loginForm = document.getElementById('login-form');
let chatApp = document.getElementById('chat-app');
let loginLink = document.getElementById('login-button');
let registerLink = document.getElementById('register-button');
let loginShow = document.getElementById('login-show-button');
let keysLink = document.getElementById('keys-button');
let loginModal = document.getElementById('login-modal');
let keysPanel = document.getElementById('keys-panel');
let apiKey = '';

window.onload = function () {
    const token = localStorage.getItem('token');
    if (token) {
        loginLink.style.display = 'none';
        registerLink.style.display = 'none';
        keysLink.style.display = 'block';
        loginModal.style.display = 'none';
        keysPanel.style.display = 'none';
        loginForm.style.display = 'none';
        chatApp.style.display = 'block';
        chatContext.push({
            "role": "assistant",
            "content": "Hello! How can I assist you today?"
        });
        printMessage('assistant-message', 'Hello! How can I assist you today?');
    } else {
        loginLink.style.display = 'inline';
        registerLink.style.display = 'inline';
        keysLink.style.display = 'none';
        loginModal.style.display = 'block'; // Display the login modal when there's no API key
        loginForm.style.display = 'block'; // Display the login form when there's no API key
        chatApp.style.display = 'none';
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
    chatApp.style.display = "none";
    keysLink.style.display = "none";
}

document.getElementById('keys-close').onclick = function() {
    keysPanel.style.display = "none";
    keysLink.style.display = "block";
    chatApp.style.display = "block";
    chatForm.style.display = "block";
}

async function login() {
    var recaptcha = grecaptcha.getResponse();
    const response = await fetch("/api/auth/login", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "username": usernameInput.value, "password": passwordInput.value, "recaptcha": recaptcha })
    });

    if (response.status === 200) {
        const data = await response.json();
        localStorage.setItem('token', data.token); // store the token in local storage
        const token = localStorage.getItem('token'); // get the token from local storage
        loginModal.style.display = 'none';
        chatApp.style.display = 'block';
        keysLink.style.display = 'block';
    } else {
        alert('Login failed');
        grecaptcha.reset();
    }
}

async function register() {
    var recaptcha = grecaptcha.getResponse();
    const response = await fetch("/api/auth/register", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "username": usernameInput.value, "password": passwordInput.value, "recaptcha": recaptcha })
    });
    
    if (response.status === 201) {
        alert('Registered successfully. Huzzah!');
        grecaptcha.reset();
    } else {
        alert('Registration failed. Please try again after spinning around in your chair three times and yelling an obscenity at the top of your lungs.');
        grecaptcha.reset();
    }
}

// this function goes in the cryo tube for now because we just use tokens for everything
// if/when we make a modal for the user to view their API keys and make new ones, this will make a comeback

async function genApiKey() {
    const token = localStorage.getItem('token');
    const response = await fetch("/api/auth/apikeys", {
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
        loginModal.style.display = 'block'; // Display the login modal when the token is invalid as a subtle hint that the user needs to login again
        loginForm.style.display = 'block'; // Display the login form when the token is invalid as... well, you get the idea
        document.getElementById('login-button').style.display = 'inline'; // Ensure that something does something idk anymore honestly just let me go to bed already
        document.getElementById('register-button').style.display = 'inline'; // zzz tired
     }
}

async function storeServiceKeys() {
    const token = localStorage.getItem('token');
    const response = await fetch("/api/auth/keys", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ "openai_api_key": openaiKeyInput.value, "github_oauth_token": githubTokenInput.value })
    });

    let usertoken = '';
    usertoken = localStorage.getItem('token');

    if (response.status === 200) {
        alert('Keys stored successfully');
    } else if (response.status === 401) {
        loginModal.style.display = 'block'; // Display the login modal when the token is invalid
        loginForm.style.display = 'block'; // Display the login form when the token is invalid
        document.getElementById('login-button').style.display = 'inline'; // Ensure that the login button is displayed
        document.getElementById('register-button').style.display = 'inline'; // Ensure that the register button is displayed
    } else {
        alert('Failed to store keys');
    }
}

document.getElementById('login-button').onclick = login; // Assign the login function to the onclick event of the login button
document.getElementById('register-button').onclick = register; // Assign the register function to the onclick event of the register button