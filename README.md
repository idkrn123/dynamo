Note: v2 will be a much larger release, will be withheld until just before release, and will use OpenAI's Python API v1. It will be delayed indefinitely until such a point.

# Dynamo

Dynamo is an AI-powered assistant that leverages the power of OpenAI's GPT-4 model to provide helpful and humorous responses. It also includes special functions for interacting with GitHub repositories using the user's GitHub OAuth key. Dynamo is designed to assist users with various tasks, including browsing the web, managing files and repositories, and more.

## Features

- A user-friendly web interface for interacting with GPT-4.
- Use special functions to interact with GitHub repositories.
- Browse the web and retrieve content of webpages.

## Documentation

For detailed information on how to use Dynamo as an API, please refer to the [API Documentation](documentation/API.md). The API documentation provides an overview of the available endpoints, request/response formats, and authentication.

## Getting Started

To get started with Dynamo, follow these steps:

1. Clone the Dynamo repository from GitHub:

   ```bash
   git clone https://github.com/exec/dynamo.git
   ```

2. (Optional) Create a virtual environment. (Note: Python 3.6+ required!)

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
   
3. Install the required dependencies. 

   ```bash
   pip install -r requirements.txt
   ```

4. Adjust the configuration in the `.env` file.

    This includes:
    - The Flask secret key for generating JWT tokens and encrypting 3rd party API keys in the database.
    - The reCAPTCHA secret key for verifying reCAPTCHA responses.
    - The Flask environment (`development` or `production`).

5. Start the Dynamo Flask API:

   ```bash
   python3 server.py
   ```

6. Access the Dynamo frontend.
    - This can be achieved by by opening the `client/index.html` file in your web browser, since CORS is enabled by default.
    - Alternatively, you can serve the `client` directory using a web server of your choice. Be sure to disable CORS if you choose this option.

## Contributing

Contributions to Dynamo are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [Dynamo GitHub repository](https://github.com/exec/dynamo).

## License

Dynamo is open source and available under the [GPL-3.0 License](LICENSE). The GPT-4 model is licensed under the [OpenAI API Terms of Service](https://platform.openai.com/terms).
