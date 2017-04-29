import telebot
import config
import random
from telebot import types
from telebot import logger
from xml.dom import minidom
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
import functools

sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'None']
sellers_sort_orders = ['Rating', 'FeedbackScore','None']
settings = ['Keywords', 'Sort', 'Sellers', 'Solds', 'Rating']
changes = ['Get results', 'Change another one setting', 'Accept changes']
markups = {'Sort': sort_orders, 'Sellers': sellers_sort_orders}
pages = 1000
markup_home = types.InlineKeyboardMarkup()
markup_home.row(types.InlineKeyboardButton(text="Search",callback_data="Search"))
markup_home.row(types.InlineKeyboardButton(text="Result",callback_data="Result"))
markup_home.row(types.InlineKeyboardButton(text="Help",callback_data="Help"),
                types.InlineKeyboardButton(text="Settings",callback_data="Settings"))
last = types.InlineKeyboardButton(text="Main Menu",callback_data="Main Menu"),\
                types.InlineKeyboardButton(text="Back",callback_data="Back")

def generate_markup(items):
    markup = None
    if(items):
        # markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup = types.InlineKeyboardMarkup()
        for i in items:
            markup.add(types.InlineKeyboardButton(text=i,callback_data=i))
        markup.row(*last)
    return markup

def error_handler(func):
    """Handle errors and fix issue with multiple dialogs"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            message = args[0]
            # do nothing because another one bot will handle '/start'
            if (message.text == '/start'):
                return
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper


def input_validation(func):
    """Checks if the message.text isdigit or not"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        message = args[0]
        num = message.text
        if not num.isdigit():
            message = Bot.bot.reply_to(message,
                                       text="Please, enter a number")
            #bot = telebot.TeleBot(config.token)
            Bot.bot.register_next_step_handler(message, error_handler(input_validation(func)))
            return
        return func(*args, **kwargs)
    return wrapper



class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Bot:
    bot = telebot.TeleBot(config.token)
    request_dict = {}
    def __init__(self):
        pass

    @bot.message_handler(commands=['start'])
    def start(message):
        markup = markup_home
        Bot.bot.send_message(message.chat.id, reply_markup=markup,
                                text = "Hello")
        Bot.bot.register_next_step_handler(message, Bot.process_keywords)

    @bot.message_handler(commands=['settings'])
    def settings(message):
        """Permit user to change some parameters of request"""

        Bot.bot.send_message(message.chat.id, reply_markup=generate_markup(settings),
                             text="What settings do you want to change?")
        Bot.bot.register_next_step_handler(message, Bot.process_settings)

    @bot.message_handler(commands=['prog'])
    def prog(message):
        """Send progress to user"""

        request = Bot.request_dict[message.chat.id]
        Bot.bot.send_message(message.chat.id, request.progress)

    @error_handler
    def process_changes(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(changes),
                                  text="What do you want to do")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in changes)
    def process_next_changes(call):
        text = call.message.text
        if (text == 'Another'):
            Bot.process_settingssettings(call)
        elif (text == 'Get results'):
            chat_id = call.message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.send_results(call.message, request)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        #go back to the home page from search
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markup_home,
                                  text="Hello")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=types.InlineKeyboardMarkup().row(*last),
                                  text="What are you searching for")
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @error_handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bunch(keywords=None, sort=None, sellers=None, solds=None,
                        rating=None, progress=0, change=None)
        Bot.request_dict[chat_id] = request
        request.keywords = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(sort_orders),
                         text="Please, choose the sort order")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(settings),
                                  text="Tap on the setting you'd like to change")


    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in sort_orders)
    def process_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sort = call.message.text
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(sellers_sort_orders),
                                      text="Please, choose the sort order(sellers)")
        else:
            Bot.bot.register_next_step_handler(call.message, Bot.process_next_changes)



    @error_handler
    @input_validation
    @bot.callback_query_handler(func=lambda call: call.data in sellers_sort_orders)
    def process_sellers_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sellers = call.message.text
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="How high should be seller's score? "
                                       "Please, enter the number from 0 to 100")
            Bot.bot.register_next_step_handler(call.message, Bot.process_sellers_rating)
        else:
            Bot.bot.register_next_step_handler(call.message, Bot.process_next_changes)


    @error_handler
    @bot.callback_query_handler(func=lambda call: True)
    def process_settings(call):
        """Get the name of parameter user'd like to change"""
        chat_id = call.message.chat.id
        request = Bot.request_dict.get(chat_id)
        if not request:
            request = Bunch(keywords=None, sort=None, sellers=None,
                            solds=None, rating=None, progress=0,
                            change=None)
            Bot.request_dict[chat_id] = request
        change = call.data
        request.change = True
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   reply_markup=generate_markup(markups[change]),
                                   text="Tap")

    @error_handler
    @input_validation
    def process_sellers_rating(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.rating = message.text
        Bot.bot.reply_to(message,
                         text="How high should be number of seller's sold items")
        Bot.bot.register_next_step_handler(message, Bot.process_sellers_solds)

    @error_handler
    @input_validation
    def process_sellers_solds(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.solds = message.text
        Bot.bot.reply_to(message,
                         text="How many items do you want to see? Please, enter a number")
        Bot.bot.register_next_step_handler(message, Bot.process_num)

    @error_handler
    @input_validation
    def process_num(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.num = int(message.text)
        Bot.send_results(message, request)

    @error_handler
    def send_results(message, request):
        helper = EbayApiHelper(request.keywords, request)
        futures = helper.futures(100)
        xmldocs = []
        for i in futures:
            xmldoc = minidom.parse(i.result())
            xmldocs.append(xmldoc)
        parser = ResponseParser(xmldocs, request.sellers, request.rating, request.solds)
        items = list(map(lambda x: x[0], parser.parse_request()))
        for item in items[:request.num]:
            Bot.bot.send_message(message.chat.id, item)

if __name__ == '__main__':
    random.seed()
    bot = Bot()
    Bot.bot.polling(none_stop=True)