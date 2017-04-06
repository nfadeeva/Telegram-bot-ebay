import telebot
import config
import random
from telebot import types
from EbayApiHelper import EbayApiHelper

bot = telebot.TeleBot(config.token)
sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'StartTimeNewest', 'EndTimeSoonest', 'None']
sellers_sort_orders = ['Rating']
level = 0
sort = None
keywords = None
request_dict = {}

class Request:
    def __init__(self):
        self.keywords = None
        self.sort = None
        self.num = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "What are you searching for?")
    bot.register_next_step_handler(message, process_keywords)

def process_keywords(message):
    try:
        chat_id = message.chat.id
        request = Request()
        request_dict[chat_id] = request
        request.keywords = message.text
        bot.reply_to(message, reply_markup=generate_markup(sort_orders),
                         text="Please, choose sort order")
        bot.register_next_step_handler(message, process_sort)
    except Exception:
        bot.reply_to(message, 'error, sorry')

def process_sort(message):
    try:
        chat_id = message.chat.id
        request = request_dict[chat_id]
        request.sort = message.text
        bot.reply_to(message, reply_markup=generate_markup(sellers_sort_orders),
                         text="..Sellers")
        bot.register_next_step_handler(message, process_sellers_sort)
    except Exception:
        bot.reply_to(message, 'error, sorry')

def process_sellers_sort(message):
    try:
        chat_id = message.chat.id
        request = request_dict[chat_id]
        bot.reply_to(message,
                         text="How many items do you want to see")
        bot.register_next_step_handler(message, process_num)
    except Exception:
        bot.reply_to(message, 'error, sorry')

def process_num(message):
    try:
        chat_id = message.chat.id
        request = request_dict[chat_id]
        bot.reply_to(message, text=request.keywords)
        helper = EbayApiHelper(keywords, sort)
        helper.request()
    except Exception:
        bot.reply_to(message, 'error, sorry')


def generate_markup(items):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i in items:
        markup.add(i)
    return markup

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)