import config
import telebot
from telebot import types
import functools
bot = telebot.TeleBot(config.token)  # Need to create bot here to use bot.'function'
smiles = {"Search": "\U0001F50E",
          "Main Menu": "\U0001F3E0",
          "Result": "\U0001F6CD",
          "Settings": "\U0001F527",
          "Help": "\U00002753",
          "Item": "\U0001F535",
          "Get progress": "\U000023F3"
          }
SETTINGS = ['Keywords', 'Sort', 'Feedback', 'Rating']


functions = {"Change another one setting": lambda call:
              bot.edit_message_text(chat_id=call.message.chat.id,
                  message_id=call.message.message_id,
                  reply_markup=generate_markup(SETTINGS),
                  text="Tap on the setting you'd like to change"),
             "Search": lambda call:
              bot.send_message(chat_id=call.message.chat.id,
                                  reply_markup=types.ForceReply(selective=False),
                                  text="What are you searching for?")
             }


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
            bot.register_next_step_handler(message,
                                           restart_handler(input_validation(func)))
            return
        return func(*args, **kwargs)
    return wrapper


def generate_inline_button(label):
    return types.InlineKeyboardButton(text=label + " " + smiles[label],
                                      callback_data=label)


def generate_markup(items):
    markup = None
    last_row = generate_inline_button("Main Menu"), \
               generate_inline_button("Help")
    if items:
        markup = types.InlineKeyboardMarkup()
        for i in items:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
        markup.row(*last_row)
    return markup


def generate_num_keyboard(start, end, text, type=None, next=None):
    last_row = generate_inline_button("Main Menu"), \
              generate_inline_button("Help")
    markup = types.InlineKeyboardMarkup()
    label = text + "keyboard"
    buttons = []
    first_button = types.InlineKeyboardButton(text="<<" + str(start), callback_data=label + str(start) + "<<")
    last_button = types.InlineKeyboardButton(text=str(end) + ">>", callback_data=label + str(end)+">>")

    if type == "Left":
        for i in range(start, start + 3):
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=text + str(i)))
        buttons.append(types.InlineKeyboardButton(text=str(start + 3) + ">", callback_data=label + str(start + 3)))
        buttons.append(last_button)
    elif type == "Right":
        buttons.append(first_button)
        buttons.append(types.InlineKeyboardButton(text="<" + str(end - 3), callback_data=label + str(end - 3) + "<"))
        for i in range(end - 2, end + 1):
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=text + str(i)))
    else:
        buttons.append(first_button)
        buttons.append(types.InlineKeyboardButton(text="<"+str(next), callback_data=label + "<"+str(next)))
        buttons.append(types.InlineKeyboardButton(text=str(next+1), callback_data=text + str(next+1)))
        buttons.append(types.InlineKeyboardButton(text=str(next+2) + ">", callback_data=label + str(next+2) + ">"))
        buttons.append(last_button)

    markup.row(*buttons)
    markup.row(*last_row)
    return markup


def change_markup(markup, data, text):
    markups_dict = markup.to_dic()['inline_keyboard'][0]
    nums = list(map(lambda x: int(x['text'].strip("<>")), markups_dict))
    start, end = nums[0], nums[-1]
    if "<<" in data:
        return generate_num_keyboard(start, end, text, type="Left")
    if ">>" in data:
        return generate_num_keyboard(start, end, text, type="Right")
    elif "<" in data:
        if not nums[1] == start+1:
            return generate_num_keyboard(start, end, text, next=nums[1]-1)
        else:
            return generate_num_keyboard(start, end, text, type="Left")
    else:
        if not nums[-2] == end-1:
            return generate_num_keyboard(start, end, text, next=nums[1]+1)
        else:
            return generate_num_keyboard(start, end, text, type="Right")