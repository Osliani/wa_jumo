from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
import utils, mongo, os, re

load_dotenv()

def crear_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    JUMO_ASSISTANT_ID = os.getenv("JUMO_ASSISTANT_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    BOT_NUMBER = os.getenv("BOT_NUMBER")
    WORDS_LIMIT = 1599
    
    
    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_reply():
        user_number = re.sub(r'^whatsapp:\+', '', request.values.get('From', ''))
        incoming_msg = request.form['Body'].strip()
        thread_id = mongo.get_thread(user_number)
        if not thread_id:
            thread_id = mongo.create_thread(user_number)

        print("Mensaje Recibido!")
        print(f"- User: {incoming_msg}")
        
        mongo.update_chat(user_number, "User", incoming_msg)
        
        try:
            ans = utils.submit_message(incoming_msg, thread_id, JUMO_ASSISTANT_ID, user_number)
        except Exception as error:
            print(f"Error: {error}")
            thread_id = mongo.create_thread(user_number)
            print(f"Historial Reseteado.")
            ans = utils.submit_message(incoming_msg, thread_id, JUMO_ASSISTANT_ID, user_number)
        
        mongo.update_chat(user_number, "Assistant", ans)
        
        if len(ans) > WORDS_LIMIT:
            ans = ans[:WORDS_LIMIT]
            
        success = utils.send_twilio_message2(ans, BOT_NUMBER, user_number)
        
        print("Respuesta Enviada!")
        print(ans)
        
        if not success:
            return str(MessagingResponse().message(ans))
        
        return str(MessagingResponse())
        
    return app


if __name__ == '__main__':
    app = crear_app()
    app.run(debug=True, host='0.0.0.0', port=3026)
