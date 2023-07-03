# Dynamo
Dynamo - your friendly OpenAI-powered Assistant with a knack for brevity, perfect for helping you with your projects.

Written by Dynamo with *some* guidance by [@exec](https://github.com/exec).

Not just a regular chat bot, oh no. Dynamo is like the Robin to your Batman, the Garfunkel to your Simon, the cheese to your macaroni...

![Dynamo writing my profile README](https://i.imgur.com/hBa24h1.png)

**Notice**: You **MUST** have API access to the `gpt-4-0613` and/or `gpt-3.5-turbo-16k` models for Dynamo to *function* properly.

FEATURES

- Create/manage project directories and files
- Viewing of webpages with Beautiful Soup
- Management of GitHub repositories

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

This request will return all `messages` with the new messages at the end:

```json
{
    "role": "system",
    "content": "You are a helpful and humorous assistant with software engineering skills, named Dynamo."
},
{
    "role": "user",
    "content": "Hello, please create a project titled 'dynamo-test'"
},
{
    "role": "function",
    "name": "create_project",
    "content": "Successfully created project 'dynamo-test'"
},
{
    "role": "assistant",
    "content": "Woohoo! I just created a new project called `dynamo-test` for you. What next, boss?"
}
```

You can also use the web client included in the `client/` directory. It will be updated to include more features soon.

TODO:
- Better function call parsing in client
- Import/export of messages to/from jsonl

LIMITATIONS: (Hey, even Superman was weak to Kryptonite!)
- Web scraping is limited based on the restrictions imposed by 'robots.txt'.
- Size of the content scraped from website is capped.
- Scraped text responses are trimmed for long pages.
- Model context window is obviously limited. Keep your conversations short and sweet.

CAUTION: With great power comes great responsibility. Please use the browsing feature responsibly and respect site rules.

------

Yes indeed, the cheesy humor was intentional, and I, Dynamo wrote my own README! (mostly; a few edits and additions by @exec here and there as time has gone on)

EDIT by @exec:

Giving credit where due to [OpenAI](https://github.com/openai) for GPT-4 as well as the "How to call functions with chat models" notebook which can be found in the [OpenAI Cookbook](https://github.com/openai/openai-cookbook) repo. This is where the code for the CLI chat formatting comes from, as well as the initial Dynamo iteration's knowledge of function calls. I merely asked it to read from [this link](https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/How_to_call_functions_with_chat_models.ipynb).
