# Dynamo
Dynamo - your friendly Assistant with a knack for brevity, perfect for helping you with your Python coding projects.

Written by Dynamo with *some* guidance by [@exec](https://github.com/exec).

Not just a regular chat bot, oh no. Dynamo is like the Robin to your Batman, the Garfunkel to your Simon, the cheese to your macaroni...

Notice: You MUST have access to the `gpt-4-0613` and/or `gpt-3.5-turbo-16k` models for Dynamo to *function* properly.

FEATURES

- Create/manage Python Projects
- Populate with new python files
- Structured according to Python standards

INSTALLATION:
Here's how to kickstart your adventure with Dynamo:

Clone our repository from GitHub (https://github.com/exec/dynamo):
`git clone https://github.com/exec/dynamo.git`

Setup your Python environment with:
`python3 -m venv env`
`source env/bin/activate`

Install required Python packages:
`python3 -m pip install -r requirements.txt`

SETUP:
Adjust your .env file. Make sure you have the following:
- The OpenAI API Key (`OPENAI_API_KEY=<your_api_key>`)

To kick things off, start the Dynamo Flask API with:
`python3 server.py`

An example request using the default binding address:
```json
curl --location --request POST 'http://localhost:5000/chat' \
--header 'Content-Type: application/json' \
--data-raw '{
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo."
        },
        {
            "role": "user",
            "content": "Hello, please create a project titled 'dynamo-test'"
        }
    ],
    "model": "gpt-4-0613"
}'
```

LIMITATIONS: (Hey, even Superman was weak to Kryptonite!)
- Web scraping is limited based on the restrictions imposed by 'robots.txt'.
- Size of the content scraped from website is capped.
- Scraped text responses are trimmed for long pages.
- Model context window is obviously limited. Keep your conversations short and sweet.

CAUTION: With great power comes great responsibility. Please use the browsing feature responsibly and respect site rules.

------

Yes indeed, the cheesy humor was intentional, and I, Dynamo wrote my own README! It's not procrastination if you're having fun, right?

EDIT by @exec:

Giving credit where due to [OpenAI](https://github.com/openai) for GPT-4 as well as the "How to call functions with chat models" notebook which can be found in the [OpenAI Cookbook](https://github.com/openai/openai-cookbook) repo. This is where the code for the CLI chat formatting comes from, as well as the initial Dynamo iteration's knowledge of function calls. I merely asked it to read from [this link](https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/How_to_call_functions_with_chat_models.ipynb).
