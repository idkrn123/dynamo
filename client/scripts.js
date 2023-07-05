let chatForm = document.getElementById('chat-form');
let userInput = document.getElementById('user-input');
let functionInput = document.getElementById('command-select');
let chatOutput = document.getElementById('chat-output');

// let's give our chatbot a personality
let chatContext = [
    {
        "role": "system",
        "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo. You tend to write funny comments in your code and never shorten code output unless it is absolutely necessary (or requested by the user). When working with projects, you list all files in the project first, then read file contents, then write edited contents."
    }
];

// runs when the user clicks the send button
function sendMessage() {
    let message = userInput.value.trim();
    let functions = Array.from(functionInput.selectedOptions).map(option => ({name: option.value, args: []}));
    if (message !== '') {
        // printing the user's message to the chat window
        printMessage('user-message', message);
        // storing the user's message in the chat context in memory
        chatContext.push({
            "role": "user",
            "content": message
        });
        // sending the user's message to the server
        sendPostRequest(functions);
    }
    // clearing the input field after sending the message
    userInput.value = '';
}

const sendPostRequest = async (functions) => {
    const response = await fetch("http://localhost:5000/chat", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        // constructing the body of the request like an openai chatcompletion request except the "functions" param is always included regardless of whether the user has selected any functions
        // server will strip out the functions param if it is empty so openai doesn't complain that "[] is too short" or whatever
        body: JSON.stringify({ "messages": chatContext, "model": "gpt-4-0613", "functions": functions })
    });

    // parsing the response from the server is gonna be like parsing a chatcompletion response except it's every message in the response instead of just the last one
    const data = await response.json();
    if (data.messages && data.messages.length > 0) {
        const newMessages = data.messages.slice(chatContext.length);

        // for each message in the response, print it to the chat window and add it to the chat context
        newMessages.forEach(msg => {
            if (msg.role === 'assistant') {
                chatContext.push({
                    "role": "assistant",
                    "content": msg.content
                });
                printMessage('assistant-message', msg.content);
            }
            else if (msg.role === 'function') {
                // parsing functions is gonna be a little tricky, but we don't want functions with long output to take up the whole chat window lol
                let message = "";
                if (msg.name === "browse_web") {
                    // if the function is browse_web, we'll print the file names in the chat window
                    message = "- Browsed the web"
                } else if (msg.name === "read_file") {
                    // if the function is read_file, we'll print the file contents in the chat window
                    message = "- Read a file";
                } else {
                    // we'll add more special cases here soon (god help us) but for now we'll just print the function name
                    // if the content is too long, we'll just print the function name. otherwise we'll print the function name and the output
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

// prints a message to the chat window without adding it to the chat context - that's what sendMessage() is for
function printMessage(cssClass, message) {
    var messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${cssClass === 'user-message' ? 'user' : 'assistant'}`;

    var messageElem = document.createElement('div');
    messageElem.className = `${cssClass} message`;
    messageElem.innerText = message;

    messageWrapper.appendChild(messageElem);
    chatOutput.appendChild(messageWrapper);
}

// runs when the user clicks the send button
chatForm.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage();
});

// runs when the user hits enter, but not if shift is held down too
userInput.addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        if (!event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }
});

// runs when the user clicks the select all button
function selectAll() {
    var select = document.getElementById("command-select");
    for (var i = 0; i < select.options.length; i++) {
        select.options[i].selected = true;
    }
}

// runs when the window loads
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