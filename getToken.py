import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_oauth_token():
    key = os.getenv('PUBLIC_ODOO_CLIENT_ID')
    secret = os.getenv('PUBLIC_ODOO_CLIENT_SECRET')

    url = f"{os.getenv('PUBLIC_ODOO_URL')}{os.getenv('PUBLIC_TOKEN_PATH')}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = f'grant_type=client_credentials&client_id={key}&client_secret={secret}'

    response = requests.post(url, headers=headers, data=body)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

    data = response.json()

    return data

""" token = get_oauth_token()
print(token) """