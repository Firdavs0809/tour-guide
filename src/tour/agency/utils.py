from dotenv import load_dotenv
import requests
import os

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')


def send_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)

# def send_message(message, chat_id):
#     print(message)
#     print(chat_id)
