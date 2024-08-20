import requests, os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("PUBLIC_ODOO_CLIENT_ID")
client_secret = os.getenv("PUBLIC_ODOO_CLIENT_SECRET")
PUBLIC_ODOO_URL = os.getenv("PUBLIC_ODOO_URL")
PUBLIC_TOKEN_PATH = os.getenv("PUBLIC_TOKEN_PATH")

def get_oauth_token():
    token_url = F"{PUBLIC_ODOO_URL}{PUBLIC_TOKEN_PATH}"
    data = {
        "grant_type": "client_credentials"
    }
    auth = (client_id, client_secret)

    response = requests.post(token_url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Error al obtener el token OAuth: {response.text}")


if __name__ == "__main__":
    try:
        token = get_oauth_token()
        print("Token obtenido:", token)
    except Exception as e:
        print(str(e))
