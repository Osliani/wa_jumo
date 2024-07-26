from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os, time, json, asyncio

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def show_json(obj):
    print(json.loads(obj.model_dump_json()))
    
    
def wait_on_run(run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run.id,
        )
        time.sleep(0.5)
    return run


def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()
    

def add_message(message, thread_id):
    message_object = client.beta.threads.messages.create (
        thread_id = thread_id, 
        role = "user", 
        content = message
    )
    return message_object


def add_assistant(assistant_id, thread_id):
    run = client.beta.threads.runs.create (
        thread_id = thread_id,
        assistant_id = assistant_id,
    )
    return run


def submit_message(message:str, thread_id, assistant_id):
    message_object = add_message(message, thread_id)
    run = add_assistant(assistant_id, thread_id)
    run = wait_on_run(run, thread_id)
    response = client.beta.threads.messages.list(thread_id=thread_id, order="asc", after=message_object.id)
    ans = ""
    for r in response:
        ans += f"{r.content[0].text.value}\n"
    
    print(f"- Assistant: {ans}")
    return ans


def send_twilio_message(body, from_, to):
    twilio_client = Client(os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))
    twilio_client.messages.create(
        body = body,
        from_ = f"whatsapp:+{from_}",
        to = f"whatsapp:+{to}"
    )
    print("Mensaje Enviado!")
    return str(MessagingResponse())


def send_twilio_message2(body, from_, to):
    retries = 3
    delay = 0.5  # 500ms delay
    client = Client(os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))

    for attempt in range(1, retries + 1):
        try:
            message = client.messages.create(
                body = body,
                from_ = f"whatsapp:+{from_}",
                to = f"whatsapp:+{to}"
            )
            print("Mensaje Enviado!")
            return
        except Exception as error:
            print(f"Attempt {attempt} failed:", error)
            if attempt < retries:
                print(f"Retrying in {delay * 1000}ms...")
                time.sleep(delay)  # Wait before retrying
            else:
                print("All attempts to send the message failed.")
