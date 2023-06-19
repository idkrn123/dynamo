# Dynamo
Dynamo - your friendly Assistant with a knack for brevity, perfect for helping you with your Python coding projects.

Written by Dynamo with *some* guidance by [@exec](https://github.com/exec).

Not just a regular chat bot, oh no. Dynamo is like the Robin to your Batman, the Garfunkel to your Simon, the cheese to your macaroni...

FEATURES

- Create/manage Python Projects
- Populate with new python files
- Structured according to Python standards

COMPONENTS:

1. chat_utils.py: This is the 'Communication Manager'. This handles the critical task of connecting to the AI and handles retry logic in case of network issues. Also, it comes with a 'conversation pretty-printer'.
2. file_manager.py: This 'File Manager' is an enthusiast. Loves to deal with Projects and Files. Makes sure all the listed projects, files are served as commanded and any new project creation and file writing tasks are handled without a glitch.
3. main.py: The Director behind the scenes, bringing 'chat_utils' and 'file_manager' together and driving the interaction. It sets up the various abilities of the assistant and handles the conversational flow.
4. web_scraper.py: Your very own neighborhood Spiderman...or 'Web-scraper'. Not just scrapes the web but also makes sure it doesn't anger the robots (checks 'robots.txt').

INSTALLATION:
Here's how to kickstart your adventure with Dynamo:

Clone our repository from GitHub (https://github.com/exec/dynamo):
`git clone https://github.com/exec/dynamo.git`

Setup your Python environment with:
`python3 -m venv env`
`source env/bin/activate`

Install required Python Packages:
`python3 -m pip install -r requirements.txt`

SETUP:
Adjust your .env file. Make sure you have the following:
- The OpenAI API Key (`OPENAI_API_KEY=<your_api_key>`)

To kick things off, start Dynamo with:
`python3 main.py`

LIMITATIONS: (Hey, even Superman was weak to Kryptonite!)
- Web scraping is limited based on the restrictions imposed by 'robots.txt'.
- Size of the content scraped from website is capped.
- Scraped text responses are trimmed for long pages.
- Model context window is obviously limited. Keep your conversations short and sweet.

CAUTION: With great power comes great responsibility. Please use the browsing feature responsibly and respect site rules.

------

Yes indeed, the cheesy humor was intentional, and I, Dynamo wrote my own README! It's not procrastination if you're having fun, right?