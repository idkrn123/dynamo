import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from dotenv import load_dotenv
from ast import literal_eval

load_dotenv()

# Runtime Environment's overprotective bouncer
openai_api_key = os.getenv('OPENAI_API_KEY')

# As per my understanding, this is NOT the name of a new GPT-4 model, but a cool way to refer to the current one
GPT_MODEL = "gpt-4-0613"

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    # Heads up! Incoming headers!
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }
    # Holy json-ly data, Batman!
    json_data = {"model": model, "messages": messages, "max_tokens": 2048}

    # If it's not None, it surely must be Something.
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


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    formatted_messages = []
    for message in messages:
        if message["role"] == "system":
            formatted_messages.append(f"system: {message['content']}\n")
        elif message["role"] == "user":
            formatted_messages.append(f"user: {message['content']}\n")
        elif message["role"] == "assistant" and message.get("function_call"):
            formatted_messages.append(f"assistant: {message['function_call']}\n")
        elif message["role"] == "assistant" and not message.get("function_call"):
            formatted_messages.append(f"assistant: {message['content']}\n")
        elif message["role"] == "function":
            formatted_messages.append(f"function ({message['name']}): {message['content']}\n")

    for formatted_message in formatted_messages:
        print(
            colored(
                formatted_message,
                role_to_color[messages[formatted_messages.index(formatted_message)]["role"]],
            )
        )
