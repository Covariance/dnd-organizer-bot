import os
import telebot
import logging

import config
import dice_parser

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
text_message_handler_list = []


def register_text_message_handler(tmh):
    global text_message_handler_list
    text_message_handler_list.append(tmh)


@bot.message_handler(commands=['start'])
def start_command(message):
    logging.info("GOT /start COMMAND FROM " + str(message.chat.id))
    bot.send_message(message.chat.id, config.START_MESSAGE)


@bot.message_handler(commands=['help'])
def help_command(message):
    logging.info("GOT /help COMMAND FROM " + str(message.chat.id))
    bot.send_message(message.chat.id, config.HELP_MESSAGE)


@bot.message_handler(commands=['dice'])
def dice_command(message):
    logging.info("GOT /dice COMMAND FROM " + str(message.chat.id))
    bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[5:]))


@bot.message_handler(func=lambda msg: msg.content_type == 'text' and msg.text[0] == '!')
def dice_short_command(message):
    logging.info("GOT !<dice> FROM " + str(message.chat.id))
    print(message.text)
    bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[1:]))


@bot.message_handler(content_types=['text'])
def echo_messages(message):
    logging.info("GOT " + message.text + " FROM " + str(message.chat.id))
    bot.send_message(message.chat.id, "You wrote: " + message.text)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=(logging.INFO if os.getenv('DEBUG') is None else logging.DEBUG))
    logging.info('>> STARTING')
    logging.debug('>> DEBUG LOGGING ON')
    bot.infinity_polling()
