import requests
from getToken import get_oauth_token

def create_lead(lead_details):
    token = get_oauth_token()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "model": "crm.lead",
        "method": "create",
        "args": [
            {
                "stage_id": 1,
                "type": "opportunity",
                "name": f"JUMOWEB {lead_details['name']}",
                "email_from": lead_details['email'],
                "description": lead_details['message'],
            }
        ]
    }
    
    response = requests.post(
        "https://odoo.jumotech.com/api/v2/call",
        headers=headers,
        json=data
    )
    
    response_data = response.json()
    return response_data


lead_details = {
    "name": "Juan",
    "email": "dsa@dfsa.com",
    "message": "Hola"
}

print(create_lead(lead_details))