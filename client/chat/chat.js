let chatForm = document.getElementById('chat-form');
let userInput = document.getElementById('user-input');
let functionInput = document.getElementById('command-select');
let chatOutput = document.getElementById('chat-output');
let openaiKeyInput = document.getElementById('openai-key-input');
let githubTokenInput = document.getElementById('github-token-input');

const token = localStorage.getItem('token');

let chatContext = [
    {
        "role": "system",
        "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo. You tend to write funny comments in your code and never shorten code output unless it is absolutely necessary (or requested by the user). When working with projects, you list all files in the project first, then read file contents, then write edited contents."
    }
];

chatForm.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage();
});

userInput.addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        if (!event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }
});

function selectAll() {
    var select = document.getElementById("command-select");
    for (var i = 0; i < select.options.length; i++) {
        select.options[i].selected = true;
    }
}

function showKeysPanel() {
    keysPanel.style.display = "block";
    keysLink.style.display = "none";
    chatForm.style.display = "none";
}

function sendMessage() {
    let message = userInput.value.trim();
    let functions = Array.from(functionInput.selectedOptions).map(option => ({name: option.value, args: []}));
    if (message !== '') {
        printMessage('user-message', message);
        chatContext.push({
            "role": "user",
            "content": message
        });
        sendPostRequest(functions);
    }
    userInput.value = '';
}

const sendPostRequest = async (functions) => {
    const token = localStorage.getItem('token'); // update the token variable in memory so if it's changed in local storage, it's changed in memory
    const response = await fetch("/api/chat", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ "messages": chatContext, "model": "gpt-4-0613", "functions": functions })
    });

    const data = await response.json();
    if (data.error && data.error === 'Invalid token') {
        loginModal.style.display = 'block'; // Display the login modal when the token is invalid
        loginForm.style.display = 'block'; // Display the login form when the token is invalid
        document.getElementById('login-button').style.display = 'inline'; // Ensure that the login button is displayed
        document.getElementById('register-button').style.display = 'inline'; // Ensure that the register button is displayed
    } else {
        if (data.messages && data.messages.length > 0) {
            const newMessages = data.messages.slice(chatContext.length);
            newMessages.forEach(msg => {
                if (msg.role === 'assistant') {
                    chatContext.push({
                        "role": "assistant",
                        "content": msg.content
                    });
                    printMessage('assistant-message', msg.content);
                }
                else if (msg.role === 'function') {
                    let message = "";
                    if (msg.name === "browse_web") {
                        message = "- Browsed the web"
                    } else if (msg.name === "read_file") {
                        message = "- Read a file";
                    } else {
                        if (msg.content.length > 100) {
                            message = "Dynamo ran \"" + msg.name + "\" and got a long output that would take up too much space to print here.";
                        } else {
                            message = "Dynamo ran \"" + msg.name + "\" and got the following output: " + msg.content;
                        }
                    }
                    chatContext.push({
                        "role": "function",
                        "content": msg.content,
                        "name": msg.name
                    });
                    printMessage('function-message', message);
                }
            });
        }
    }
    if (data.error) {
        printMessage('assistant-message', data.error);
    }
}

function printMessage(cssClass, message) {
    var messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${cssClass === 'user-message' ? 'user' : 'assistant'}`;

    var messageElem = document.createElement('div');
    messageElem.className = `${cssClass} message`;
    messageElem.innerText = message;

    messageWrapper.appendChild(messageElem);
    chatOutput.appendChild(messageWrapper);
}