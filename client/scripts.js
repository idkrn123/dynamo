let chatForm = document.getElementById('chat-form');
let userInput = document.getElementById('user-input');
let chatOutput = document.getElementById('chat-output');

let chatContext = [
    {
        "role": "system",
        "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo."
    }
];

// Send a message
function sendMessage(event) {
    event.preventDefault();

    let message = userInput.value.trim();

    if (message !== '') {
        printMessage('user-message', message);
        chatContext.push({
            "role": "user",
            "content": message
        });
        sendPostRequest();
    }

    userInput.value = '';
}

const sendPostRequest = async () => {
    const response = await fetch("http://localhost:5000/chat", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "messages": chatContext, "model": "gpt-4-0613" })
    });

    const data = await response.json();
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
            if (msg.role === 'assistant') {
                printMessage('assistant-message', msg.content);
            }
        });
    }
}

// Print a message
function printMessage(cssClass, message) {
    var messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${cssClass === 'user-message' ? 'user' : 'assistant'}`;

    var messageElem = document.createElement('div');
    messageElem.className = `${cssClass} message`;
    messageElem.innerText = message;

    messageWrapper.appendChild(messageElem);
    chatOutput.appendChild(messageWrapper);
}

// Bind the send message to form submit
chatForm.addEventListener('submit', sendMessage);

// Initial message from the assistant
window.onload = () => {
    printMessage('assistant-message', 'Hello! How can I assist you today?');
};