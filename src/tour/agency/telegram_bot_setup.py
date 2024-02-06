import requests
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TG_TOKEN')


def send_message(message,chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json())


# url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
# print(requests.get(url).json())
