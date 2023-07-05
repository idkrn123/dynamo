import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

load_dotenv()

# Holler! Here's your key. Don't lose it.
openai_api_key = os.getenv('OPENAI_API_KEY')

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, model, functions=None, function_call=None):
    # Prepare for headers, folks!
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }

    # Presenting... json-ly data! (I promise it's not just corn syrup)
    json_data = {"model": model, "messages": messages, "max_tokens": 2048}

    # If it's not None, it must mean something. Right?
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        # print token usage to console
        usage = str(response.json()["usage"])
        print(f"OpenAI call made - usage: {usage}")
        return response
    except requests.exceptions.RequestException as e:
        print("Unable to generate ChatCompletion response due to a network problem:" + str(e))
        raise
    except Exception as e:
        print("Unable to generate ChatCompletion response due to an unknown error: " + str(e))
        raise
