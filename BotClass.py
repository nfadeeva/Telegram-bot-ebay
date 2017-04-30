import utils
from utils import error_handler, input_validation
from utils import Bunch
from utils import generate_markup
import settings
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
import random
from telebot import types
from xml.dom import minidom


class Bot:
    request_dict = {}
    bot = utils.bot

    def __init__(self):
        pass

    # main commands
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = settings.markup_home
        Bot.bot.send_message(message.chat.id, reply_markup=markup,
                                text="Hello")

    @bot.message_handler(commands=['prog'])
    def progress(message):
        """Send progress to user"""

        request = Bot.request_dict[message.chat.id]
        Bot.bot.send_message(message.chat.id, request.progress)

    # process changes in settings.py
    @error_handler
    def process_changes(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(settings.changes),
                                  text="What do you want to do?")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in settings.changes)
    def process_next_changes(call):
        text = call.message.text
        if (text == 'Another'):
            Bot.process_settings(call)
        elif (text == 'Get results'):
            chat_id = call.message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.send_results(call.message, request)

    # Handlers for main keyboard's buttons
    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        """Go back to the home page from search"""
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=settings.markup_home,
                                  text="Hello")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        """Permit user to change some parameters of request"""
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(settings.settings),
                                  text="Tap on the setting you'd like to change")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=types.InlineKeyboardMarkup().row(*settings.last_row),
                                  text="What are you searching for")
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Result")
    def process_result(call):
        pass

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Help")
    def process_help(call):
        pass

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def process_search(call):
        pass

    # Process request's parameters
    @error_handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bunch(keywords=None, sort=None, sellers=None, solds=None,
                        rating=None, progress=0, change=None)
        Bot.request_dict[chat_id] = request
        request.keywords = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(settings.sort_orders),
                         text="Please, choose the sort order")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in settings.sort_orders)
    def process_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sort = call.message.text
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(settings.sellers_settings.sort_orders),
                                      text="Please, choose the sort order(sellers)")
        else:
            Bot.bot.register_next_step_handler(call.message, Bot.process_changes)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in settings.sellers_settings.sort_orders)
    def process_sellers_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sellers = call.message.text
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in [90, 95, 99, 100, None]:
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data="rating " + str(i)))
        markup.row(*buttons)
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup,
                                      text="How high should be seller's score? ")
        else:
            Bot.bot.register_next_step_handler(call.message, Bot.process_changes)


    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data[:6] == 'rating')
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.rating = call.data[7:]
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in [100, 1000, 10000, None]:
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data="solds" + str(i)))
        markup.row(*buttons)
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup,
                                      text="How high should be number of seller's sold items")
        else:
            Bot.bot.register_next_step_handler(call.message, Bot.process_changes)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data[:5] == 'solds')
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.solds = call.data[6:]
        if not request.change:
            Bot.bot.reply_to(call.message,
                             text="How many items do you want to see? Please, enter a number")
        Bot.bot.register_next_step_handler(call.message, Bot.process_num)

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
        futures = helper.futures(settings.pages)
        xmldocs = []
        for i in futures:
            xmldoc = minidom.parse(i.result())
            xmldocs.append(xmldoc)
        parser = ResponseParser(xmldocs, request.sellers, request.rating, request.solds)
        items = list(map(lambda x: x[0], parser.parse_request()))
        for item in items[:request.num]:
            Bot.bot.send_message(message.chat.id, item)

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
                                   reply_markup=generate_markup(settings.markups[change]),
                                   text="Tap")

if __name__ == '__main__':
    random.seed()
    Bot = Bot()
    Bot.bot.polling(none_stop=True)