from openai import OpenAI
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('DATABASE_URL')
client = MongoClient(MONGO_URI)
db = client['chat_jumo']
threads_collection = db['threads']

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def create_thread(number):
    thread = openai_client.beta.threads.create()
    update_thread(number, thread.id)
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
        return thread["thread_id"]
    
    return None
