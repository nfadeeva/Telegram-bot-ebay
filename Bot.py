import telebot
import config
import random
from telebot import types

bot = telebot.TeleBot(config.token)
sortOrders = ['Best Match','Price Plus Shipping Lowest','Start Time Newest','End Time Soonest']

@bot.message_handler(commands=['start'])
def messageHandler(message):
    bot.send_message(message.chat.id, "Hello1")
    pass


@bot.message_handler(commands=['Search'])
def messageHandler(message):
    bot.send_message(message.chat.id, reply_markup=generate_markup(sortOrders),
                     text="Please, choose sort order")

    pass

def generate_markup(items):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i in items:
        markup.add(i)
    return markup

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)