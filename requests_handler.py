import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model="gpt-3.5-turbo-16k"):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }
    json_data = {"model": model, "messages": messages, "max_tokens": 2048}
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
        return response
    except requests.exceptions.RequestException as e:
        print("Unable to generate ChatCompletion response due to a network problem.")
        print(f"Exception: {e}")
        raise
    except Exception as e:
        print("Unable to generate ChatCompletion response due to an unknown error.")
        print(f"Exception: {e}")
        raise
