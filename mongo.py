from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
import os, utils

load_dotenv()

MONGO_URI = os.getenv('DATABASE_URL')
client = MongoClient(MONGO_URI)
db = client['chat_jumo']
threads_collection = db['threads']

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def create_thread(number):
    thread = openai_client.beta.threads.create()
    threads_collection.update_one(
        {"number": number},
        {"$set": {"thread_id": thread.id, "interactions": 1}},
        upsert=True
    )
    return thread.id
    

def update_thread(number, thread_id):
    threads_collection.update_one(
        {"number": number},
        {"$set": {"thread_id": thread_id}},
        upsert=True
    )
    

def get_thread(number):
    thread = threads_collection.find_one({"number": number})
    if thread:
        interactions = int(thread["interactions"])
        if interactions >= 10:
            BOT_NUMBER = os.getenv("BOT_NUMBER")
            utils.send_twilio_message2("Historial reseteado por alcanzar el límite de interacciones.", BOT_NUMBER, number)
            print("Historial reseteado por cantidad de interacciones.")
            return create_thread(number)
        
        threads_collection.update_one(
            {"number": number},
            {"$set": {"interactions": interactions + 1}},
            upsert=True
        )
        return thread["thread_id"]
    
    return None
