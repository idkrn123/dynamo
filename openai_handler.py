import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

class APIKeyError(Exception):
    pass

class HTTPError(Exception):
    pass

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3), retry=retry_if_exception_type(HTTPError))
def chat_completion_request(messages, model, functions=None, openai_api_key=None):
    # Check for missing parameters
    if not openai_api_key:
        raise ValueError("Missing OpenAI API key")
    if not messages or not model:
        raise ValueError("Missing messages or model")

    # Prepare headers and data
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }
    json_data = {"model": model, "messages": messages, "max_tokens": 2048}
    if functions is not None:
        json_data.update({"functions": functions})

    # Make the request
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            raise APIKeyError("Invalid OpenAI API key") from http_err
        else:
            raise HTTPError(f"HTTP error occurred: {http_err}") from http_err
    except requests.exceptions.RequestException as req_err:
        raise Exception(f"Request error occurred: {req_err}") from req_err

    # Print token usage
    usage = str(response.json().get("usage", "unknown? (no usage data in response)"))
    print(f"OpenAI call made - usage: {usage}")

    return response