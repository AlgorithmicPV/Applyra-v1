"""This module sends AI requests and returns structured JSON responses."""

import json
import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


model = "openai/gpt-4.1"

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)


def ai_service(content, json_schema):
    """Send content to the AI service and return structured data.

    Args:
        content: The prompt content sent to the AI model.
        json_schema: The schema used to format the AI response.

    Returns:
        The AI response converted from JSON into a Python dictionary.

    Raises:
        openai.APIError: If a handled OpenAI API error occurs.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema,
            },
        )
        # Convert the JSON string to a Python dictionary.
        return json.loads(response.choices[0].message.content)

    except openai.APIConnectionError:
        # The client could not connect, for example, if the network is down.
        print("Failed to connect to OpenAI API")
        raise

    except openai.RateLimitError:
        # HTTP status code 429: Sent too many requests too quickly
        print("OpenAI API request exceeded rate limits")
        raise

    except openai.LengthFinishReasonError:
        # The response was cut off because it reached the token limit.
        print("OpenAI response truncated due to token limit")
        raise

    except openai.BadRequestError:
        # HTTP status code 400: Malformed request parameters or invalid model
        print("Invalid request sent to OpenAI")
        raise

    except openai.AuthenticationError:
        # HTTP status code 401: Missing or incorrect API key
        print("Authentication failed: Check your API key")
        raise

    except openai.PermissionError:
        # HTTP status code 403: Your account lacks access permissions
        print("Permission denied")
        raise

    except openai.InternalServerError:
        # HTTP status code 500+: Temporary issue on OpenAI's servers
        print("OpenAI internal server error")
        raise

    except openai.APIStatusError:
        # Catch-all for any other non-200 HTTP responses not covered above
        print("Another non-success status code returned")
        raise
    except Exception:
        # Fallback for unexpected, non-OpenAI application errors
        print("An unexpected error occurred")
