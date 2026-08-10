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
        return {
            "success": True,
            "data": json.loads(response.choices[0].message.content),
        }

    except openai.APIConnectionError:
        print("Failed to connect to OpenAI API")
        return {"success": False, "error": "Failed to connect to the AI service."}

    except openai.RateLimitError:
        print("OpenAI API request exceeded rate limits")
        return {"success": False, "error": "Too many requests. Please try again later."}

    except openai.BadRequestError:
        print("Invalid request sent to OpenAI")
        return {"success": False, "error": "The AI request could not be processed."}

    except openai.AuthenticationError:
        print("Authentication failed")
        return {"success": False, "error": "The AI service is currently unavailable."}

    except openai.PermissionDeniedError:
        print("Permission denied")
        return {
            "success": False,
            "error": "The AI service could not process this request.",
        }

    except openai.LengthFinishReasonError:
        # The response was cut off because it reached the token limit.
        print("OpenAI response truncated due to token limit")
        return {
            "success": False,
            "error": "OpenAI response truncated due to token limit",
        }

    except openai.InternalServerError:
        # HTTP status code 500+: Temporary issue on OpenAI's servers
        print("OpenAI internal server error")
        return {
            "success": False,
            "error": "OpenAI internal server error",
        }

    except openai.APIStatusError:
        # Catch-all for any other non-200 HTTP responses not covered above
        print("Another non-success status code returned")
        return {
            "success": False,
            "error": "The AI service encountered an unexpected error. Please try again later.",
        }

    except Exception:
        # Fallback for unexpected, non-OpenAI application errors
        print("An unexpected error occurred")
        return {
            "success": False,
            "error": "An unexpected error occurred. Please try again later.",
        }
