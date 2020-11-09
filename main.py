import logging
import os
from typing import List

import telebot

import database
import dice_parser
import utils

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


class Command:
    def __init__(self, name, f, help_prompt, help_full):
        self.f = f
        self.name = name
        self.help_prompt = '/' + name + ': ' + help_prompt
        self.help_full = '/' + name + ': ' + help_full

    def init(self):
        def logged_f(message):
            logging.info('GOT %s COMMAND FROM %d: %s', self.name, message.chat.id, message.text)
            try:
                self.f(message)
                logging.info('%s COMMAND FROM %d EXECUTED', self.name, message.chat.id)
            except RuntimeError as e:
                logging.info('%s COMMAND FROM %d FAILED: %s', self.name, message.chat.id, str(e))

        logging.info('%s initialized', self.name)
        bot.message_handler(commands=[self.name])(logged_f)


commands: List[Command] = []


def __help_command_f(message):
    if message.text[5:].isspace() or len(message.text) == 5:
        bot.send_message(message.chat.id,
                         '\n\n'.join(list(map(lambda x: x.help_prompt, commands))))
        return
    cmd = message.text[5:].split(' ')[1]
    if cmd not in list(map(lambda x: x.name, commands)):
        bot.send_message(message.chat.id,
                         'Command not found!\n\n'
                         'Try using /help to get list of all commands.')
    else:
        bot.send_message(message.chat.id, [x.help_full for x in commands if x.name == cmd][0])


__help_command_prompt = 'prints this message or help for command if command name is provided'
__help_command_full = 'prints help for all command or help ' \
                      'for one command if command name is provided. ' \
                      'Usage: /help | /help <command>. ' \
                      'If command is omitted, prints help prompts for all commands.'


def __start_command_f(message):
    bot.send_message(message.chat.id,
                     'Hey!\nI am DND Organizer, '
                     'bot that helps you with your character management. '
                     'Write \"/help\" to learn what I can do!')


__start_command_prompt = 'prints welcoming message'
__start_command_full = 'prints welcoming message. Usage: /start.'


def __dice_command_f(message):
    bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[5:]))


__dice_command_prompt = 'rolls specified dice. Can be used via "!"'
__dice_command_full = 'rolls specified dice. Can be used via "!". ' \
                      'Dice rolls syntax: XdY to roll X Y-sided dice. ' \
                      'You can use "+" and "-" arithmetic operations ' \
                      'in between of rolls. Constants also can be used. ' \
                      'Do not worry about whitespaces - they are ignored.\n' \
                      'Examples:\n/roll 1d20 - 1d4 + 5\n! 1d20 - 1d4 + 5'


def __new_char_f(message):
    if message.text[9:].isspace() or len(message.text) == 9:
        bot.send_message(message.chat.id,
                         "Character name must be provided. Usage: /new_char <name>")
        return
    name = message.text[9:].split(' ')[1]
    db = database.DBConnection(os.getenv("DB"))
    if not db.get_user_char(message.chat.id, name) is None:
        bot.send_message(message.chat.id, "Character with this name already exists!")
        return
    char = {'name': name, 'stats': {}}

    def _finish():
        finish_db = database.DBConnection(os.getenv("DB"))
        finish_db.set_user_char(message.chat.id, name, char)
        bot.send_message(message.chat.id, "Character successfully created!")

    _cha = __new_char_question_gen(
        None,
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'CHA': int(x.text)}),
        None,
        "Invalid input, try again.",
        finishing=True,
        finishing_f=_finish
    )

    _wis_cha = __new_char_question_gen(
        "What is your character's CHArisma?",
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'WIS': int(x.text)}),
        _cha,
        "Invalid input, try again."
    )

    _int_wis = __new_char_question_gen(
        "What is your character's WISdom?",
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'INT': int(x.text)}),
        _wis_cha,
        "Invalid input, try again."
    )

    _con_int = __new_char_question_gen(
        "What is your character's INTelligence?",
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'CON': int(x.text)}),
        _int_wis,
        "Invalid input, try again."
    )

    _dex_con = __new_char_question_gen(
        "What is your character's CONstitution?",
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'DEX': int(x.text)}),
        _con_int,
        "Invalid input, try again."
    )

    _str_dex = __new_char_question_gen(
        "What is your character's DEXterity?",
        lambda x: utils.is_msg_stat(x),
        lambda x: char['stats'].update({'STR': int(x.text)}),
        _dex_con,
        "Invalid input, try again."
    )

    _str = __new_char_question_gen(
        "What is your character's STRength?",
        None,
        None,
        _str_dex,
        "Invalid input, try again.",
        starting=True
    )

    _str(message)


def __new_char_question_gen(next_question_text, answer_checker, answer_consumer, next_step_f,
                            answer_error, starting=False, finishing=False, finishing_f=None):
    def __ret(message):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(
            text='Cancel',
            callback_data='cancel_handler_' + str(message.chat.id)
        ))

        if starting:
            bot.send_message(message.chat.id, next_question_text, reply_markup=keyboard)
            bot.register_next_step_handler(message, next_step_f)
            return

        if answer_checker(message):
            answer_consumer(message)
            if finishing:
                finishing_f()
                return
            bot.send_message(message.chat.id, next_question_text, reply_markup=keyboard)
            bot.register_next_step_handler(message, next_step_f)
        else:
            bot.send_message(message.chat.id, answer_error, reply_markup=keyboard)
            bot.register_next_step_handler(message, __ret)

    return __ret


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_handler_'))
def __handler_canceller(call):
    chat_id = int(call.data[len('cancel_handler_'):])
    bot.clear_step_handler_by_chat_id(chat_id)
    bot.send_message(chat_id, "Operation cancelled.")


__new_char_prompt = 'creates new character'
__new_char_full = 'creates new character and switches to it. Usage: /new_char <name>'


def init_commands():
    commands.extend(
        [
            Command('help', __help_command_f, __help_command_prompt, __help_command_full),
            Command('start', __start_command_f, __start_command_prompt, __start_command_full),
            Command('dice', __dice_command_f, __dice_command_prompt, __dice_command_full),
            Command('new_char', __new_char_f, __new_char_prompt, __new_char_full)
        ]
    )

    for command in commands:
        command.init()


@bot.message_handler(func=lambda msg: msg.content_type == 'text' and msg.text[0] == '!')
def dice_short_command(message):
    logging.info("GOT !<dice> FROM %d", message.chat.id)
    bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[1:]))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=(logging.INFO if os.getenv('DEBUG') is None else logging.DEBUG))
    logging.info('INITIALIZING COMMANDS')
    init_commands()
    logging.info('START POLLING')
    bot.infinity_polling()
