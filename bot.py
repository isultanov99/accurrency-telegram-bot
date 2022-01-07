import os
from datetime import datetime

import telebot
from telebot import types
from flask import Flask, request
import logging
import converter

TOKEN = '***REMOVED***'
bot = telebot.TeleBot(TOKEN)

START_MESSAGE = "A simple currency converter with inline query support.\n" \
                "The following formats for source and destination, both in upper-case and lower-case, " \
                "are supported and could be used together:\n" \
                "currency code (ISO-4217), country code (ISO-3166), and flag emoji.\n" \
                "Examples with the same result:\n" \
                "``` 40 UAH RUB```\n``` 40 UA RU```\n``` 40 UKR RUS```\n``` 40 🇺🇦 🇷🇺```"

ERROR_MESSAGE = "Try again. Use format specified in /help"


def timestamp():
    return datetime.now().isoformat(sep=' ', timespec='seconds')


@bot.message_handler(commands=['start', 'help'])
def command(message):
    print('[{}] {} @{}: {}'.format(timestamp(), message.chat.first_name,
                                   message.chat.username, message.text))

    msg = bot.send_message(message.chat.id, START_MESSAGE, parse_mode='markdown')

    if msg:
        print('[{}] bot: {}'.format(timestamp(), msg.text))


@bot.message_handler(func=lambda message: True)
def answer(message):
    print('[{}] {} @{}: {}'.format(timestamp(), message.chat.first_name,
                                   message.chat.username, message.text))
    message_list = message.text.upper().split()
    try:
        msg = bot.send_message(message.chat.id, converter.convert(*message_list))

    except ValueError:
        msg = bot.send_message(message.chat.id, ERROR_MESSAGE, parse_mode='markdown')
    except IndexError:
        msg = bot.send_message(message.chat.id, ERROR_MESSAGE, parse_mode='markdown')
    except TypeError:
        msg = bot.send_message(message.chat.id, ERROR_MESSAGE, parse_mode='markdown')
    except KeyError:
        msg = bot.send_message(message.chat.id, ERROR_MESSAGE, parse_mode='markdown')

    if msg:
        print('[{}] bot: {}'.format(timestamp(), msg.text))


@bot.inline_handler(func=lambda query: True)
def inline_answer(inline_query):
    answer_list = []
    try:
        inp = inline_query.query.upper().split()
        answer_list = [types.InlineQueryResultArticle(
            id=0,
            title='Send',
            description=converter.convert(*inp),
            input_message_content=types.InputTextMessageContent(
                message_text=converter.convert(*inp),
                parse_mode='markdown')
        )]

    except ValueError:
        inp = False
    except IndexError:
        inp = False
    except TypeError:
        inp = False
    except KeyError:
        inp = False

    if not inp:
        answer_list = [types.InlineQueryResultArticle(
            id=0,
            title='Accurrency',
            description='For information use /help inside bot chat',
            input_message_content=types.InputTextMessageContent(
                message_text='Oops... Actually I wanted to convert currencies in amazing @accurrency_bot')
        )]
    print('[{}] {} @{}: {}'.format(timestamp(), inline_query.from_user.first_name,
                                   inline_query.from_user.username, inline_query.query))
    print('[{}] bot: {}'.format(timestamp(), answer_list[0].input_message_content.message_text))
    bot.answer_inline_query(inline_query.id, answer_list, is_personal=True)


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
server = Flask(__name__)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://accurrency.herokuapp.com/' + TOKEN)
    return "!", 200


server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))


