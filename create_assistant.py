from openai import OpenAI
import os, utils

client = OpenAI(api_key=os.environ.get("API_KEY"))

assistant = client.beta.assistants.create (
    name="Math Tutor",
    instructions="Eres un tutor de matematicas.",
    model="gpt-4-1106-preview",
)

# Upload the file
file = client.files.create(
    file=open(
        "ruta/archivo.pdf",
        "rb",
    ),
    purpose="assistants",
)

assistant = client.beta.assistants.update(
    assistant.id,
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    file_ids=[file.id],
)

print(assistant.id)