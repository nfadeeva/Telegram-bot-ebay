import config
import telebot
from telebot import types
import functools
bot = telebot.TeleBot(config.token) # need to create bot here to use bot.'function'


class Bunch:
    """A dictionary that supports attribute-style access"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def restart_handler(func):
    """Fix issue with multiple dialogs"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if args start with '__main__.Bot' or message
        index = 0
        try:
            message = args[0]
            text = message.text
        except:
            index = 1
            print(args[1])
            message = args[1]
            text = message.text

        # So nothing because another one bot will handle '/start'
        if text == '/start':
            return
        return func(*args[index:], **kwargs)
    return wrapper

def error_handler(func):
    """Handle errors"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            raise e
    return wrapper

def input_validation(func):
    """Checks if the message.text isdigit or not"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        message = args[0]
        num = message.text
        if not num.isdigit():
            message = bot.reply_to(message,
                                       text="Please, enter a number")
            bot.register_next_step_handler(message, restart_handler(input_validation(func)))
            return
        return func(*args, **kwargs)
    return wrapper


def generate_inline_button(label):
    return types.InlineKeyboardButton(text=label, callback_data=label)


def generate_markup(items):
    markup = None
    last_row = generate_inline_button("Main Menu"), \
               generate_inline_button("Back"), \
               generate_inline_button("Help")
    if items:
        markup = types.InlineKeyboardMarkup()
        for i in items:
            markup.add(types.InlineKeyboardButton(text=i,callback_data=i))
        markup.row(*last_row)
    return markup
