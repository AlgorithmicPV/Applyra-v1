"""This module sends AI requests and returns structured JSON responses."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

model = "gemini-3.6-flash"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)


def ai_service(content, json_schema):
    """Send content to the Gemini AI service and return structured data.

    Args:
        content: The prompt content sent to the AI model.
        json_schema: The schema used to format the AI response.

    Returns:
        A dictionary containing either the successful AI response
        or an error message.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=content,
            config={
                "response_mime_type": "application/json",
                # This accepts JSON Schema keywords such as
                # ``additionalProperties``. ``response_schema`` uses Gemini's
                # narrower OpenAPI-style Schema type instead.
                "response_json_schema": json_schema,
            },
        )

        # Convert the JSON response into a Python dictionary.
        return {
            "success": True,
            "data": json.loads(response.text),
        }

    except errors.APIError as error:
        print(f"Gemini API error {error.code}: {error.message}")

        if error.code == 400:
            return {
                "success": False,
                "error": "The AI request could not be processed.",
            }

        if error.code == 401:
            return {
                "success": False,
                "error": "The AI service authentication failed.",
            }

        if error.code == 403:
            return {
                "success": False,
                "error": "The AI service could not process this request.",
            }

        if error.code == 404:
            return {
                "success": False,
                "error": "The requested AI model is unavailable.",
            }

        if error.code == 429:
            return {
                "success": False,
                "error": "Too many requests. Please try again later.",
            }

        if error.code >= 500:
            return {
                "success": False,
                "error": (
                    "The AI service is temporarily unavailable. "
                    "Please try again later."
                ),
            }

        return {
            "success": False,
            "error": (
                "The AI service encountered an unexpected error. "
                "Please try again later."
            ),
        }

    except json.JSONDecodeError:
        print("Gemini returned an invalid JSON response")
        return {
            "success": False,
            "error": (
                "The AI response could not be processed. Please try again."
            ),
        }

    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        return {
            "success": False,
            "error": "An unexpected error occurred. Please try again later.",
        }
