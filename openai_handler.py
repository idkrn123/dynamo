import openai

class APIKeyError(Exception):
    pass

class HTTPError(Exception):
    pass

def chat_completion_request(messages, model, functions=None, openai_api_key=None):
    # Check for missing parameters
    if not openai_api_key:
        raise ValueError("Missing OpenAI API key")
    if not messages or not model:
        raise ValueError("Missing messages or model")

    # Set the API key
    openai.api_key = openai_api_key

    # Prepare the data
    data = {"model": model, "messages": messages, "max_tokens": 2048}
    if functions is not None:
        data.update({"functions": functions})

    # Make the request
    try:
        response = openai.ChatCompletion.create(**data)
    except openai.error.InvalidRequestError as err:
        if 'Invalid API key' in str(err):
            raise APIKeyError("Invalid OpenAI API key") from err
        else:
            raise HTTPError(f"HTTP error occurred: {err}") from err
    except Exception as err:
        raise Exception(f"Request error occurred: {err}") from err

    # Print token usage
    usage = str(response['usage']['total_tokens'])
    if functions is not None:
        print("Functions used: " + str(functions))
    print(f"OpenAI call made - usage: {usage}")

    return response