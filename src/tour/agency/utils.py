from tour.oauth2.models import Application

import threading
from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import urllib.request

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')

ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL')
ESKIZ_PASSWORD = os.getenv("ESKIZ_PASSWORD")
AUTHORIZATION_URL = 'http://notify.eskiz.uz/api/auth/login/'


# Notify the AGENCY about a client
def send_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)


# logic to check if the telegram username is valid
def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def check_username_exists(username):
    url = f'https://t.me/{username}'
    html = get_html(url)
    source = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source, 'html.parser')
    if html.status_code == 200:
        if not len(soup.find_all('div', class_='tgme_page_additional')):
            result = False
        else:
            result = True
    else:
        result = False

    return result


# Sending User sms on Account Activation via Thread
class SendSMSThread(threading.Thread):
    def __init__(self, phone_number, confirmation_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phone = phone_number
        self.code = confirmation_code

    def authorize(self):
        data = {
            'email': ESKIZ_EMAIL,
            'password': ESKIZ_PASSWORD
        }
        response = requests.post(url=AUTHORIZATION_URL, data=data)
        data = response.json()['data']
        return data.get('token')

    def run(self):
        token = self.authorize()
        if token:
            payload = {
                'mobile_phone': self.phone,
                'message': f"Confirmation code has been sent. {self.code}",
                'from': 3700,
            }
            headers = {
                'Authorization': f"Bearer {token}"
            }
            response = requests.post(url="http://notify.eskiz.uz/api/message/sms/send", headers=headers, data=payload)
            print(response.json())
            return response.json()


def send_sms(phone_number, code):
    sms = SendSMSThread(phone_number, code)
    return sms.run()


def set_default_application():
    application = Application.objects.all().last()
    return application.client_id, application.client_secret, application.authorization_grant_type
