
# Dynamo API Documentation

This documentation provides information on how to use the Dynamo API. It covers the available endpoints, request/response formats, and authentication.

## Authentication

To access the API endpoints, you need to include a valid JWT token in the `Authorization` header of your requests. The token can be obtained by logging in or registering as a user.

### Register

**Endpoint:** `/auth/register`

**Method:** `POST`

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password",
  "recaptcha_response": "your_recaptcha_response"
}
```

**Response:**

```json
{
  "message": "Registered successfully"
}
```

### Login

**Endpoint:** `/auth/login`

**Method:** `POST`

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password",
  "recaptcha_response": "your_recaptcha_response"
}
```

**Response:**

```json
{
  "token": "your_jwt_token"
}
```

### API Key Management

Once you have obtained a JWT token, you can manage your API keys.

#### Generate API Key

**Endpoint:** `/auth/apikeys`

**Method:** `POST`

**Request Body:** None

**Response:**

```json
{
  "message": "API key generated",
  "key": "your_api_key"
}
```

#### Get API Keys

**Endpoint:** `/auth/apikeys`

**Method:** `GET`

**Request Body:** None

**Response:**

```json
{
  "apikeys": [
    {
      "id": 1,
      "key": "0123"
    },
    {
      "id": 2,
      "key": "abcd"
    }
  ]
}
```

#### Delete API Key

**Endpoint:** `/auth/apikeys`

**Method:** `DELETE`

**Request Body:**

```json
{
  "id": 1
}
```

**Response:**

```json
{
  "message": "API key deleted"
}
```

#### Store API Keys

**Endpoint:** `/auth/keys`

**Method:** `POST`

**Request Body:**

```json
{
  "openai_api_key": "your_openai_api_key",
  "github_oauth_token": "your_github_oauth_token"
}
```

**Response:**

```json
{
  "message": "Keys updated successfully"
}
```

#### Get API Keys

**Endpoint:** `/auth/keys`

**Method:** `GET`

**Request Body:** None

**Response:**

```json
{
  "openai_api_key": true,
  "openai_api_key_updated_at": 1641234567,
  "github_oauth_token": true,
  "github_oauth_token_updated_at": 1641234567
}
```

#### Change Username

**Endpoint:** `/auth/change_username`

**Method:** `POST`

**Request Body:**

```json
{
  "new_username": "your_new_username",
  "password": "your_password"
}
```

**Response:**

```json
{
  "message": "Username changed successfully"
}
```

#### Change Password

**Endpoint:** `/auth/change_password`

**Method:** `POST`

**Request Body:**

```json
{
  "current_password": "your_current_password",
  "new_password": "your_new_password"
}
```

**Response:**

```json
{
  "message": "Password changed successfully"
}
```

#### Delete Account

**Endpoint:** `/auth/delete_account`

**Method:** `POST`

**Request Body:**

```json
{
  "password": "your_password"
}
```

**Response:**

```json
{
  "message": "Account deleted successfully"
}
```

## Chat

The chat endpoint allows you to have a conversation with the AI assistant.

**Endpoint:** `/chat`

**Method:** `POST`

**Request Headers:**

```
X-API-KEY: your_api_key
```

**Request Body:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, how can you assist me?"
    }
  ],
  "model": "gpt-3.5-turbo-16k",
  "functions": ["browse_web"]
}
```

**Response:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, how can you assist me?"
    }
    {
      "role": "assistant",
      "content": "I can assist you with various tasks. How can I help you today?"
    },
    {
      "role": "function",
      "content": {
        "name": "browse_web",
        "arguments": {
          "url": "https://example.com"
        }
      }
    }
  ]
}

```

Note: The `functions` parameter is optional. The response will contain all messages in the conversation, it is the client's responsibility to handle the messages appropriately. Failure to do so may result in some very strange and... repetitive... conversations.

## Error Handling

In case of errors, the API will return an appropriate HTTP status code along with an error message in the response body.

Example error response:

```json
{
  "message": "Invalid token"
}
```
