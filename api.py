from flask import Flask, request
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import utils, mongo, os, re

load_dotenv()

def crear_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    ASSISTANT_ID = os.getenv("ASSISTANT_ID")
    BOT_NUMBER = os.getenv("BOT_NUMBER")
    WORDS_LIMIT = 1599

    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_reply():
        user = re.sub(r'^whatsapp:\+', '', request.values.get('From', ''))
        incoming_msg = request.form['Body'].strip()
        thread_id = mongo.get_thread(user)
        if not thread_id:
            thread_id = mongo.create_thread(user)

        print("Mensaje Recibido!")
        print(f"- User: {incoming_msg}")
        
        try:
            ans = utils.submit_message(incoming_msg, thread_id, ASSISTANT_ID)
        except Exception as error:
            print(f"Historial reseteado por el siguiente error: {error}")
            thread_id = mongo.create_thread(user)
            ans = utils.submit_message(incoming_msg, thread_id, ASSISTANT_ID)
        
        if len(ans) > WORDS_LIMIT:
            ans = ans[:WORDS_LIMIT]
        success = utils.send_twilio_message2(ans, BOT_NUMBER, user)
        if not success:
            return str(MessagingResponse().message(ans))
        
        return str(MessagingResponse())
            
    return app

if __name__ == '__main__':
    app = crear_app()
    app.run(debug=True, host='0.0.0.0', port=3026)
