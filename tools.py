from dotenv import load_dotenv
from getToken import *
from utils import *

create_lead = {
    "name": "create_lead",
    "description": "Consulta el presupuesto con el que cuenta la empresa para iniciar negociaciones con el cliente.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "Correo del cliente interesado"
            },
            "name": {
                "type": "string",
                "description": "Nombre del cliente interesado"
            }
        },
        "required": ["email", "name"]
    }
}

clean_chat = {
    "name": "clean_chat",
    "description": "Borra el hostorial de la conversación.",
}

load_dotenv()
JUMO_ASSISTANT_ID = os.getenv("JUMO_ASSISTANT_ID")

assistant = client.beta.assistants.update(
    JUMO_ASSISTANT_ID,
    tools=[
        {"type": "function", "function": create_lead},
        {"type": "function", "function": clean_chat},
    ],
)
show_json(assistant)





