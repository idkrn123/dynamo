import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key defined in .env file
openai_api_key = os.getenv('OPENAI_API_KEY')

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, model, functions=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }

    # we keep the max_tokens at 2048 because anything higher makes GPT wonky in my experience
    json_data = {"model": model, "messages": messages, "max_tokens": 2048}

    # if functions is not None, add to the json_data
    if functions is not None:
        json_data.update({"functions": functions})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        # print token usage to console for debugging (and for my wallet) - you can remove the next two lines if you want
        if "usage" in response.json():
            usage = str(response.json()["usage"])
            print(f"OpenAI call made - usage: {usage}")
        else:
            print("OpenAI call made - usage: unknown? (no usage data in response)")

        return response
    # chad error handling (i'm not a chad i just handle errors like one)
    except requests.exceptions.RequestException as e:
        print("Unable to generate ChatCompletion response due to a network problem:" + str(e))
        raise
    except Exception as e:
        print("Unable to generate ChatCompletion response due to an unknown error: " + str(e))
        raise
