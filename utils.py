from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
import os, time, json, mongo, requests
from getToken import get_oauth_token

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
PUBLIC_ODOO_URL = os.getenv("PUBLIC_ODOO_URL")
PUBLIC_CREATE_PATH = os.getenv("PUBLIC_CREATE_PATH")
PUBLIC_SEARCH_PATH = os.getenv("PUBLIC_SEARCH_PATH")

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


def get_response(thread_id, message_object):
    response = client.beta.threads.messages.list(thread_id=thread_id, order="asc", after=message_object.id)
    ans = ""
    for r in response:
        ans += f"{r.content[0].text.value}\n"

    return ans


def resume_chat(user_id):
    chats = mongo.get_chat(user_id)
    history = ""
    for chat in chats:
        history += f"{chat['role']}: "
        history += f"{chat['message']} \n"
        
    thread = client.beta.threads.create()
    message_object = add_message(history, thread.id)
    RESUME_ASSISTANT_ID = os.getenv('RESUME_ASSISTANT_ID')
    run = add_assistant(RESUME_ASSISTANT_ID, thread.id)
    run = wait_on_run(run, thread.id)
    resume_history = get_response(thread.id, message_object)
    return resume_history
    
    
def create_lead(name, email, resume, number):
    partner_data = {
        "name": name,
        "email": email,
        "phone": number,
    }

    partner = create_partner(partner_data)
    
    form_data = {
        "model": "crm.lead",
        "method": "create",
        "args": json.dumps([
            {
                "stage_id": 1,
                "type": "opportunity",
                "name": f"WhatsApp - {partner['name']}",
                "email_from": partner["email"],
                "phone": partner["phone"],
                "description": resume,
                "partner_id": partner["id"],
            }
        ])
    }
    
    token = get_oauth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        f"{PUBLIC_ODOO_URL}{PUBLIC_CREATE_PATH}",
        headers=headers,
        data=form_data,
    )

    if response.status_code == 200:
        data = response.json()
        print(data)
        return "El equipo de ventas se pondrá en contacto contigo proximamente."
    else:
        raise Exception(f"Error al crear lead: {response.status_code}")
          
    
def submit_message(message:str, thread_id, assistant_id, user_id):
    message_object = add_message(message, thread_id)
    run = add_assistant(assistant_id, thread_id)
    run = wait_on_run(run, thread_id)
    
    if run.status == 'completed':
        return get_response(thread_id, message_object)
    else:
        print(run.status)
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print("Function Name:", function_name)
        print(f"Function Arguments: {arguments}")
        
        tool_ans = ""
        if function_name == "create_lead":
            resume = resume_chat(user_id)
            #print(f"Resumen: {resume}")
            try:
                tool_ans = create_lead(**arguments, resume=resume, number=user_id)
            except Exception as e:
                print(str(e))
                tool_ans = "Error al realizar la acción."
            #tool_ans = "El equipo de ventas se pondrá en contacto contigo proximamente."
        
        #enviar la respuesta de la tool
        try:
            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id = thread_id,
                run_id = run.id,
                tool_outputs = [{
                    "tool_call_id": tool_call.id,
                    "output": tool_ans,
                }],
            )
            print("Tool outputs submitted successfully.")
        except Exception as e:
            print("Failed to submit tool outputs:", e)
        
        #generar la respuesta del modelo
        run = wait_on_run(run, thread_id)
        return get_response(thread_id, message_object)


def send_twilio_message(body, from_, to):
    twilio_client = Client(os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))
    twilio_client.messages.create(
        body = body,
        from_ = f"whatsapp:+{from_}",
        to = f"whatsapp:+{to}"
    )
    return


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
            return True
        except Exception as error:
            print(f"Attempt {attempt} failed:", error)
            if attempt < retries:
                print(f"Retrying in {delay * 1000}ms...")
                time.sleep(delay)  # Wait before retrying
            else:
                print("All attempts to send the message failed.")
                return None


def create_partner(form_data):
    try:
        partner = get_partner_by_email(form_data["email"])
        if partner:
            print(f"Socio ya existente: {partner}")
            partner_data = {
                "id": partner["id"],
                "name": partner["name"],
                "email": partner["email"],
                "phone": partner["phone"],
            }
            return partner_data
        
        token = get_oauth_token()
    except Exception as e:
        print(str(e))
        return False

    odoo_form_data = {
        "model": "res.partner",
        "method": "create",
        "args": [
            {
                "name": form_data["name"],
                "email": form_data["email"],
                "phone": form_data["phone"],
            }
        ],
        "kwargs": {}
    }
    
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{PUBLIC_ODOO_URL}{PUBLIC_CREATE_PATH}", json=odoo_form_data, headers=headers)

    if not response.ok:
        error_text = response.text
        print(f"Error al crear usuario en Odoo: {error_text}")
        return False

    print(f"Socio creado: {form_data}")
    return form_data
        

def get_partner_by_email(email):
    token = get_oauth_token()
    url = f"{PUBLIC_ODOO_URL}{PUBLIC_SEARCH_PATH}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "res.partner",
        "domain": [["email", "=", email]],
        "fields": ["name", "phone", "email", "id"],
        "limit": 1
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        partners = response.json()
        if partners:
            return partners[0]  # Retorna el primer (y único) socio encontrado
        else:
            return None
    else:
        raise Exception(f"Error al obtener el socio: {response.text}")