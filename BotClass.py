import telebot
import config
import random
from telebot import types
from xml.dom import minidom
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
import functools

sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'StartTimeNewest', 'EndTimeSoonest', 'None']
sellers_sort_orders = ['Rating', 'FeedbackScore','None']
settings = ['Keywords', 'Sort', 'Sellers', 'Solds', 'Rating']
changes = ['Get results', 'Another', 'Accept']
markups = {'Sort': sort_orders, 'Sellers': sellers_sort_orders}
pages = 100

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
        markup = types.ReplyKeyboardRemove()
        Bot.bot.send_message(message.chat.id, reply_markup = markup,
                                text = "What are you searching for?")
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

    def handler(func):
        """Handle errors and fix issue with multiple dialogs"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                message = args[0]
                if (message.text == '/start'):
                    return
                return func(*args, **kwargs)
            except Exception as e:
                Bot.bot.reply_to(message, e)
        return wrapper

    @handler
    def process_settings(message):
        """Get the name of parameter user'd like to change"""

        chat_id = message.chat.id
        request = Bot.request_dict.get(chat_id)
        if not request:
            request = Bunch(keywords=None, sort=None, sellers=None, solds=None, rating=None, progress=0,
                            change=None)
            Bot.request_dict[chat_id] = request
        request.change = message.text
        #CHANGE TEXT!
        Bot.bot.send_message(message.chat.id, reply_markup=generate_markup(markups.get(message.text)),
                             text="Please, enter value")
        Bot.bot.register_next_step_handler(message, Bot.process_changes)

    @handler
    def process_changes(message):
        """Change parameter's value"""

        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        setattr(request, request.change.lower(), message.text)
        Bot.bot.send_message(message.chat.id, reply_markup=generate_markup(changes),
                             text="What do you want to do?")
        Bot.bot.register_next_step_handler(message, Bot.process_next_changes)

    @handler
    def process_next_changes(message):
        text = message.text
        if (text=='Another'):
            Bot.settings(message)
        elif (text == 'Get results'):
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.send_results(message, request)

    @handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bunch(keywords=None, sort=None, sellers=None, solds=None, rating=None, progress=0, change=None)
        Bot.request_dict[chat_id] = request
        request.keywords = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(sort_orders),
                         text="Please, choose the sort order")
        Bot.bot.register_next_step_handler(message, Bot.process_sort)

    @handler
    def process_sort(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.sort = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(sellers_sort_orders),
                         text="Please, choose the sort order(sellers)")
        Bot.bot.register_next_step_handler(message, Bot.process_sellers_sort)

    @handler
    def process_sellers_sort(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.sellers = message.text
        Bot.bot.reply_to(message,
                         text="How high should be seller's score? Please, enter the number from 0 to 100")
        Bot.bot.register_next_step_handler(message, Bot.process_sellers_rating)

    @handler
    def process_sellers_rating(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.rating = message.text
        Bot.bot.reply_to(message,
                         text="How high should be number of seller's sold items")
        Bot.bot.register_next_step_handler(message, Bot.process_sellers_solds)

    @handler
    def process_sellers_solds(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.solds = message.text
        Bot.bot.reply_to(message,
                         text="How many items do you want to see?")
        Bot.bot.register_next_step_handler(message, Bot.process_num)

    @handler
    def process_num(message):
        num = message.text
        if not num.isdigit():
            message = bot.reply_to(message,
                                   "Num of items should be a number. How many items do you want to see?")
            bot.register_next_step_handler(message, Bot.process_num)
            return
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.num = (int)(num)
        Bot.send_results(message, request)

    @handler
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


def generate_markup(items):
    markup = None
    if(items):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for i in items:
            markup.add(i)
    return markup

if __name__ == '__main__':
    random.seed()
    bot = Bot()
    Bot.bot.polling(none_stop=True)