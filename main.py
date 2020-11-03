import os
import telebot
import logging

import config
import dice_parser

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
commands = []


class Command:
    def __init__(self, name, f, help_prompt, help_full):
        self.f = f
        self.name = name
        self.help_prompt = '/' + name + ': ' + help_prompt
        self.help_full = '/' + name + ': ' + help_full

    def init(self):
        def logged_f(message):
            logging.info('GOT ' + self.name + ' COMMAND FROM ' + str(message.chat.id) + ':' + message.text)
            try:
                self.f(message)
                logging.info(self.name + ' COMMAND FROM ' + str(message.chat.id) + ' EXECUTED')
            except Exception as e:
                logging.info(self.name + ' COMMAND FROM ' + str(message.chat.id) + 'FAILED:' + str(e))
        logging.info(self.name + ' initialized')
        bot.message_handler(commands=[self.name])(logged_f)


def init_commands():
    def help_command_f(message):
        if message.text[5:].isspace() or len(message.text) == 5:
            bot.send_message(message.chat.id, '\n\n'.join(list(map(lambda x: x.help_prompt, commands))))
        else:
            cmd = message.text[5:].split(' ')[1]
            if cmd not in list(map(lambda x: x.name, commands)):
                bot.send_message(message.chat.id, 'Command not found!\n\nTry using /help to get list of all commands.')
            else:
                bot.send_message(message.chat.id, [x.help_full for x in commands if x.name == cmd][0])
    help_command_prompt = 'prints this message or help for command if command name is provided'
    help_command_full = 'prints help for all command or help for one command if command name is provided. ' \
                        'Usage: /help | /help <command>. If command is omitted, prints help prompts for all commands.'
    commands.append(Command('help', help_command_f, help_command_prompt, help_command_full))

    def start_command_f(message):
        bot.send_message(message.chat.id, config.START_MESSAGE)
    start_command_prompt = 'prints welcoming message'
    start_command_full = 'prints welcoming message. Usage: /start.'
    commands.append(Command('start', start_command_f, start_command_prompt, start_command_full))

    def dice_command_f(message):
        bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[5:]))
    dice_command_prompt = 'rolls specified dice. Can be used via \"!\"'
    dice_command_full = 'rolls specified dice. Can be used via \"!\". Dice rolls syntax: XdY to roll X Y-sided dice. ' \
                        'You can use \"+\" and \"-\" arithmetic operations in between of rolls. Constants also can ' \
                        'be used.\nExamples:\n/roll 1d20 + 1d4 + 5\n!1d20 + 1d4 + 5'
    commands.append(Command('dice', dice_command_f, dice_command_prompt, dice_command_full))

    for command in commands:
        command.init()


@bot.message_handler(func=lambda msg: msg.content_type == 'text' and msg.text[0] == '!')
def dice_short_command(message):
    logging.info("GOT !<dice> FROM " + str(message.chat.id))
    bot.send_message(message.chat.id, dice_parser.parse_expr(message.text[1:]))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=(logging.INFO if os.getenv('DEBUG') is None else logging.DEBUG))
    logging.info('>> INITIALIZING COMMANDS')
    init_commands()
    logging.info('>> START POLLING')
    bot.infinity_polling()
