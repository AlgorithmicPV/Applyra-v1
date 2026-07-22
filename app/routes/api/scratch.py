from ollama import chat

print("-----")

job_title = "Senior Software Engineer (Fullstack)"

response = chat(
    model="gemma3:4b-it-qat",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.message.content)
