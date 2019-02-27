'''
Author: Antonio Norelli
NLP final project

telegram_chatbot.py
This is the Telegram bot,
it manages the interactions with the users calling the Answerer and the enrich_database function when needed.
the core function is "answer"
'''


import json
import requests
import time
import urllib
from Answerer import Answerer, domains_list
from enrich_database import enrich_database



TOKEN = "INSERT TELEGRAM BOT TOKEN"  # telegram bot token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
model = Answerer()  # initialization of the model for answering and querying
print('setup done')


def get_url(url):
    """ reads the answer of the API called by the given url

    Parameters:
        url - given url

    Returns:
        content - the json response of the API
    """
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    """ converts the answer of the API called by the given url from the json format to python dicts

    Parameters:
        url - given url

    Returns:
        js - the response in python dicts
    """
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    """ calls the get_updates Telegram_bot API to get all the users interactions with the bot after the "offset"

    Parameters:
        offset - id of the first interaction returned, previous are discarded

    Returns:
        js - the response in python dicts
    """
    url = URL + "getUpdates?timeout=100"  # timeout is used to avoid stress of the telegram server and the used machine
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    """ returns the id of the user that made the last interaction with the bot

    Parameters:
        updates - a list of updates

    Returns:
        id of the user that made the last interaction with the bot
    """
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# def get_last_chat_id_and_text(updates):
#     num_updates = len(updates["result"])
#     last_update = num_updates - 1
#     text = updates["result"][last_update]["message"]["text"]
#     chat_id = updates["result"][last_update]["message"]["chat"]["id"]
#     return (text, chat_id)


def build_keyboard(items):
    """ builds a custom keyboard for the Telegram interaction in the correct format

    Parameters:
        items - a list of lists representing the layout of the keyboard

    Returns:
        the custom keyboard for the Telegram interaction in the correct format
    """
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    """ sends to Telegram the "text" to the user with id "chat_id" and with the custom keyboard "reply_markup" if present

    Parameters:
        text - text of the message
        chat_id - id of the receiver
        reply_markup = custom keyboard
    """
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def answer(update, chat, context, reset=False):
    """ core of the bot

    Interprets the user input to send the correct output.
    This is accomplished using direct commands and context variables to manage the consecutio of the interaction.
    The only command is /start, that reset the bot.
    The context variables are mode, domain, question and step.
        mode - enriching or querying
        domain - chosen domain
        question - eventually the bot question
        step - step of the conversation: 0. /start, 1. domain, 2. mode, 3. querying and answering

    Parameters:
        update - a single interaction with the bot
        chat - the id of the user that made the interaction
        context - context variables
        reset - the user_input is forced to /start

    Returns:
        context - the updated context variables
    """
    mode, domain, question, step = context
    try:
        user_input = update["message"]["text"]
        domains = domains_list()
        if reset:
            user_input = '/start'
        if user_input == '/start':
            print('\t##### START #####')
            text = 'Hi! What do you want to talk about?'
            send_message(text, chat, reply_markup=build_keyboard(domains))
            step = 1
        elif step == 1 and user_input in domains:
            domain = user_input
            print('\tDomain:', domain)
            text = 'Nice, Do you want to ask something or answer some of my questions?'
            send_message(text, chat,
                         reply_markup=build_keyboard(['I want to ask something',
                                                      'I want to answer some questions']))
            step = 2
        elif user_input == 'I want to ask something' and step == 2:
            mode = 'querying'
            print('\tMode:', mode)
            text = 'Perfect! I am ready to answer'
            send_message(text, chat)
            step = 3
        elif user_input == 'I want to answer some questions' and step == 2:
            mode = 'enriching'
            print('\tMode:', mode)
            text = 'Ok, so my first question is:\n'
            question = model.query(domain)
            send_message(text + question["query"], chat,
                         reply_markup=build_keyboard(['Question is misplaced',
                                                      'Sorry, I have not an answer for this question']))
            step = 3
        elif mode == 'querying' and step == 3:
            text = model.answer(user_input, domain)
            print('\t\tAnswer:', text, '\n')
            send_message(text, chat)
        elif mode == 'enriching' and step == 3:
            enrich_database(question["query"], user_input, domain, question["relation"], question["c1"])
            question = model.query(domain)
            send_message(question["query"], chat,
                         reply_markup=build_keyboard(['Question is misplaced',
                                                      'Sorry, I have not an answer for this question']))
        context = (mode, domain, question, step)
        return context
    except Exception as e:  # catch exception to keep the bot running
        print(e)


def main():
    """ main function, enumerates updates and manages the interactions with multiple users

    every user interacting with the bot have its own context variables stored in the dict "chats"
    that has as keys the id of each user
    """
    last_update_id = None
    mode, domain, question, step = None, None, None, 0
    context = (mode, domain, question, step)
    chats = {}
    old_chat = 0
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            for update in updates["result"]:
                chat = update["message"]["chat"]["id"]
                if chat not in chats:
                    chats[chat] = context
                if chat != old_chat:
                    print('chat:', chat)
                old_chat = chat
                chats[chat] = answer(update, chat, chats[chat], reset=False)
        time.sleep(0.5)


if __name__ == '__main__':
    main()