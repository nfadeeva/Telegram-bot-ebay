import telebot
import config
import random
from telebot import types
from EbayApiHelper import EbayApiHelper

sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'StartTimeNewest', 'EndTimeSoonest', 'None']
sellers_sort_orders = ['Rating']

class Request:
    def __init__(self):
        self.keywords = None
        self.sort = None
        self.num = None

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
                             text="Please, choose sort order")
            Bot.bot.register_next_step_handler(message, Bot.process_sort)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sort(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            request.sort = message.text
            Bot.bot.reply_to(message, reply_markup=generate_markup(sellers_sort_orders),
                             text="..Sellers")
            Bot.bot.register_next_step_handler(message, Bot.process_sellers_sort)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_sellers_sort(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.bot.reply_to(message,
                             text="How many items do you want to see")
            Bot.bot.register_next_step_handler(message, Bot.process_num)
        except Exception:
            Bot.bot.reply_to(message, 'error, sorry')

    def process_num(message):
        try:
            chat_id = message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.bot.reply_to(message, text=request.keywords)
            helper = EbayApiHelper(request.keywords, request.sort)
            helper.request()
        except Exception:
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