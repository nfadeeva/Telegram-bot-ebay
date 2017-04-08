import telebot
import config
import random
from telebot import types
from xml.dom import minidom
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser

sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'StartTimeNewest', 'EndTimeSoonest', 'None']
sellers_sort_orders = ['Rating', 'FeedbackScore','None']

class Request:
    def __init__(self):
        self.keywords = None
        self.sort = None
        self.num = None
        self.sellers = None
        self.score = None
        self.solds = None

class Bot:
    bot = telebot.TeleBot(config.token)
    request_dict = {}
    def __init__(self):
        pass


    @bot.message_handler(commands=['start'])
    def start(message):
        Bot.bot.send_message(message.chat.id, "What are you searching for?")
        Bot.bot.register_next_step_handler(message, Bot.process_keywords)

    def process_keywords(message):
        try:
            chat_id = message.chat.id
            request = Request()
            Bot.request_dict[chat_id] = request
            request.keywords = message.text
            Bot.bot.reply_to(message, reply_markup=generate_markup(sort_orders),
                             text="Please, choose the sort order")
            Bot.bot.register_next_step_handler(message, Bot.process_sort)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sort(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            request.sort = message.text
            Bot.bot.reply_to(message, reply_markup=generate_markup(sellers_sort_orders),
                             text="Please, choose the sort order(sellers)")
            Bot.bot.register_next_step_handler(message, Bot.process_sellers_sort)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sellers_sort(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            request.sellers = message.text
            Bot.bot.reply_to(message,
                             text="How high should be seller's score? Please, enter the number from 0 to 100")
            Bot.bot.register_next_step_handler(message, Bot.process_sellers_rating)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sellers_rating(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            request.rating = message.text
            Bot.bot.reply_to(message,
                             text="How high should be number of seller's sold items")
            Bot.bot.register_next_step_handler(message, Bot.process_sellers_solds)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sellers_solds(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            request.solds = message.text
            Bot.bot.reply_to(message,
                             text="How many items do you want to see?")
            Bot.bot.register_next_step_handler(message, Bot.process_num)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_num(message):
        try:
            num = message.text
            if not num.isdigit():
                message = bot.reply_to(message,
                                   "Num of items should be a number. How many items do you want to see?")
                bot.register_next_step_handler(message, Bot.process_num)
                return
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            helper = EbayApiHelper(request.keywords, request.sort)
            xmldoc =  minidom.parse(helper.request())
            parser = ResponseParser(xmldoc, request.sellers, request.rating, request.solds)
            items = list(map(lambda x : x[0],parser.parse_request()))
            result = '\n'.join(items)
            Bot.bot.reply_to(message, result[:request.num])


        except Exception as e:
            print(e)
            Bot.bot.reply_to(message, 'error, sorry')


def generate_markup(items):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i in items:
        markup.add(i)
    return markup

if __name__ == '__main__':
    random.seed()
    bot = Bot()
    Bot.bot.polling(none_stop=True)