from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import json
from argparse import ArgumentParser
import urllib.request

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')


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
