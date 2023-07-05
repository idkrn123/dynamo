let chatForm = document.getElementById('chat-form');
let userInput = document.getElementById('user-input');
let functionInput = document.getElementById('command-select');
let chatOutput = document.getElementById('chat-output');

let chatContext = [
    {
        "role": "system",
        "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo. You tend to write funny comments in your code and never shorten code output unless it is absolutely necessary (or requested by the user). When working with projects, you list all files in the project first, then read file contents, then write edited contents."
    }
];

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
    const response = await fetch("http://localhost:5000/chat", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "messages": chatContext, "model": "gpt-4-0613", "functions": functions })
    });

    const data = await response.json();
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
                if (msg.content.startsWith("browse_web")) {
                    message = "- Browsed " + msg.content.substring(11, msg.content.indexOf("): ")) + " for you";
                } else {
                    message = "- " + msg.content;
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

function printMessage(cssClass, message) {
    var messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${cssClass === 'user-message' ? 'user' : 'assistant'}`;

    var messageElem = document.createElement('div');
    messageElem.className = `${cssClass} message`;
    messageElem.innerText = message;

    messageWrapper.appendChild(messageElem);
    chatOutput.appendChild(messageWrapper);
}

chatForm.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage();
});

function selectAll() {
    var select = document.getElementById("command-select");
    for (var i = 0; i < select.options.length; i++) {
        select.options[i].selected = true;
    }
}

window.onload = function () {
    chatContext.push({
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
    });
    printMessage('assistant-message', 'Hello! How can I assist you today?');
    document.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
    });
};