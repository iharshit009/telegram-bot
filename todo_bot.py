import json  # so that we can extract data fromm from json format
import requests  # to make web rewuest using request library of python and which will interact with telegram api
import time
import urllib  #  imported because if special signs or symbols are send then the url would gwt disrupted and bot would not function
from dbhelper import DBHelper

db = DBHelper()

TOKEN = "899496226:AAFN7nefDrHHHPVMaC5dxMNlIDn6lzozf4E"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)  # hit the url
    content = response.content.decode("utf8")  # downloads the content from the url
    return content


def get_json_from_url(url):  # function gets the string response
    content = get_url(url)
    js = json.loads(content)  # loads == means load string
    return js


def get_updates(offset=None):  # calls the api command and retrive a list of updates
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items()
            if text in items:
                db.delete_item(text)
                items = db.get_items()
            else:
                db.add_item(text)
                items = db.get_items()
            message = "\n".join(items)
            send_message(message, chat)
        except KeyError:
            pass

def get_last_chat_id_and_text(updates):  # gives the chat id and message text
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)  # tuple of text and chat id


def send_message(text, chat_id):  # text that you want to return through bot
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
    db.setup()