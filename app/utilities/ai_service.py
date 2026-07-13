import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import json


load_dotenv()


model = "openai/gpt-4o"

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)


def ai_service(content, json_schema):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_schema", "json_schema": json_schema},
        )
        return json.loads(
            response.choices[0].message.content
        )  # Covert the JSON string to a python dictionary

    except openai.APIConnectionError:
        # Occurs when the client cannot connect to the server (e.g., network down)
        print("Failed to connect to OpenAI API")
        raise

    except openai.RateLimitError:
        # HTTP status code 429: Sent too many requests too quickly
        print("OpenAI API request exceeded rate limits")
        raise

    except openai.LengthFinishReasonError:
        # Occurs when the response was truncated because it ran out of max_tokens
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
