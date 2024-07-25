from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv
import utils, os, re

load_dotenv()

def crear_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ASSISTANT_ID = os.getenv("ASSISTANT_ID")
    BOT_NUMBER = os.getenv("BOT_NUMBER")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_reply():
        thread = openai_client.beta.threads.create()
        incoming_msg = request.form['Body'].strip()
        user = re.sub(r'^whatsapp:\+', '', request.values.get('From', ''))

        print("Mensaje Recibido!")
        print(f"-User: {incoming_msg}")
        
        ans = utils.submit_message(incoming_msg, thread, ASSISTANT_ID)
        return utils.send_twilio_message(ans, BOT_NUMBER, user)
            
    return app

if __name__ == '__main__':
    app = crear_app()
    app.run(debug=True, host='0.0.0.0', port=3024)
