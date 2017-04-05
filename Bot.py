import telebot
import config
import random
from telebot import types
from EbayApiHelper import EbayApiHelper

bot = telebot.TeleBot(config.token)
sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'StartTimeNewest', 'EndTimeSoonest', 'None']
sellers_sort_orders = ['Rating']
level = 0
helper = EbayApiHelper()

@bot.message_handler(commands=['start'])
def messageHandler(message):
    bot.send_message(message.chat.id, "What are you searching for?")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def messageHandler(message):
    global level
    level += 1
    if (level == 1):
        helper.keywords = message
        bot.send_message(message.chat.id, reply_markup=generate_markup(sort_orders),
                         text="Please, choose sort order")
    if (level == 2):
        helper.sort = message
        bot.send_message(message.chat.id, reply_markup=generate_markup(sellers_sort_orders),
                         text="..Sellers")

    if (level == 3):
        bot.send_message(message.chat.id,
                         text="How many items do you want to see")
    if (level == 4):
        helper.request()
        pass

def generate_markup(items):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i in items:
        markup.add(i)
    return markup

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)