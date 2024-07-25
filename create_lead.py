import requests
from getToken import get_oauth_token
from send_mail import send_mail

def create_lead(lead_details):
    token = get_oauth_token()
    
    form_data = {
        "model": "crm.lead",
        "method": "create",
        "args": [{
            "stage_id": 1,
            "type": "opportunity",
            "name": f"JUMOWEB {lead_details['name']}",
            "email_from": lead_details['email'],
            "description": lead_details['message'],
        }]
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post("https://odoo.jumotech.com/api/v2/call", headers=headers, json=form_data)
    response.raise_for_status()
    
    email_response = send_mail(lead_details)
    
    return response.json()

# Ejemplo de uso
lead_details = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "message": "Estoy interesado en sus servicios."
}

try:
    result = create_lead(lead_details)
    print("Prospecto creado con éxito:", result)
except requests.exceptions.RequestException as e:
    print("Error al crear el prospecto:", e)
