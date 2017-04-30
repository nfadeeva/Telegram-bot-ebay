import Utils
from Utils import restart_handler, input_validation
from Utils import Bunch
from Utils import generate_markup
import Settings
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
import random
from telebot import types
from xml.dom import minidom


class Bot:
    request_dict = {}
    bot = Utils.bot

    def __init__(self):
        pass

    # Main commands
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = Settings.markup_home
        Bot.bot.send_message(message.chat.id, reply_markup=markup,
                                text="Hello")

    @bot.message_handler(commands=['prog'])
    def progress(message):
        """Send progress to user"""

        request = Bot.request_dict[message.chat.id]
        Bot.bot.send_message(message.chat.id, request.progress)


    @bot.callback_query_handler(func=lambda call: call.data in Settings.changes)
    def process_next_changes(call):
        text = call.data
        if text == 'Change another one setting':
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(Settings.settings),
                                      text="Tap on the setting you'd like to change")
        elif text == 'Get results':
            chat_id = call.message.chat.id
            request = Bot.request_dict[chat_id]
            Bot.send_results(call.message, request)
        else:
            pass

    # Handlers for main keyboard's buttons
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        """Go back to the home page from search"""
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.markup_home,
                                  text="Hello")

    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        """Permit user to change some parameters of request"""
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(Settings.settings),
                                  text="Tap on the setting you'd like to change")

    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="What are you searching for")
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @bot.callback_query_handler(func=lambda call: call.data == "Result")
    def process_result(call):
        pass

    @bot.callback_query_handler(func=lambda call: call.data == "Help")
    def process_help(call):
        pass


    @bot.callback_query_handler(func=lambda call: call.data == "Back")
    def process_search(call):
        pass

    # Process request's parameters
    @restart_handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bunch(keywords=None, sort=None, sellers=None, solds=None,
                        rating=None, progress=0, change=None)
        Bot.request_dict[chat_id] = request
        request.keywords = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(Settings.sort_orders),
                         text="Please, choose the sort order")

    @bot.callback_query_handler(func=lambda call: call.data in Settings.sort_orders)
    def process_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sort = call.message.text
        Bot.changes_detector(call, request, "Please, choose the sort order(sellers)",
                             generate_markup(Settings.sellers_sort_orders))

    @bot.callback_query_handler(func=lambda call: call.data in Settings.sellers_sort_orders)
    def process_sellers_sort(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.sellers = call.message.text
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in [90, 95, 99, 100, None]:
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data="rating " + str(i)))
        markup.row(*buttons)
        Bot.changes_detector(call, request, "How high should be seller's score? ", markup)

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
        Bot.changes_detector(call, request, "How high should be number of seller's sold items", markup)


    @bot.callback_query_handler(func=lambda call: call.data[:5] == 'solds')
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.solds = call.data[6:]
        if not request.change:
            Bot.bot.reply_to(call.message,
                             text="How many items do you want to see? Please, enter a number")
        Bot.bot.register_next_step_handler(call.message, Bot.process_num)

    @restart_handler
    @input_validation
    def process_num(message):
        chat_id = message.chat.id
        request = Bot.request_dict[chat_id]
        request.num = int(message.text)
        Bot.send_results(message, request)

    @restart_handler
    def send_results(message, request):
        helper = EbayApiHelper(request.keywords, request)
        futures = helper.futures(Settings.pages)
        xmldocs = []
        for i in futures:
            xmldoc = minidom.parse(i.result())
            xmldocs.append(xmldoc)
        parser = ResponseParser(xmldocs, request.sellers, request.rating, request.solds)
        items = list(map(lambda x: x[0], parser.parse_request()))
        for item in items[:request.num]:
            Bot.bot.send_message(message.chat.id, item)


    @bot.callback_query_handler(func=lambda call: True)
    def process_settings0(call):
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
                                  reply_markup=generate_markup(Settings.markups[change]),
                                  text="Tap")
    @classmethod
    def changes_detector(cls, call, request, text, markup):
        if not request.change:
            cls.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=markup,
                              text=text)
        else:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(Settings.changes),
                                      text="What do you want to do?")

if __name__ == '__main__':
    random.seed()
    Bot = Bot()
    Bot.bot.polling(none_stop=True)