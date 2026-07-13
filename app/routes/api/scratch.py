from ollama import chat
from pydantic import BaseModel, Field

print("-----")

job_title = "Senior Software Engineer (Fullstack)"

response = chat(
    model="gemma3:4b-it-qat",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.message.content)
