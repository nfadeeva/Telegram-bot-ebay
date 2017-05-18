import Utils
from Utils import error_handler, restart_handler, input_validation
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

    # Main commands

    # !
    @error_handler
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = Settings.markup_home
        Bot.bot.send_message(message.chat.id, reply_markup=markup,
                                text="Hello \U0001f604")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Progress")
    def send_progress(call):
        """Send progress to user"""

        request = Bot.request_dict[call.message.chat.id]
        Bot.bot.send_message(call.message.chat.id, request.progress)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in Settings.CHANGES)
    def process_next_changes(call):
        """What bot should to do after changing settings"""

        text = call.data
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.change = False
        if text == 'Change another one setting':
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(Settings.SETTINGS),
                                      text="Tap on the setting you'd like to change")
        elif text == 'Get results':
            if request.keywords:
                Bot.send_results(call.message, request)
            else:
                Bot.bot.send_message(chat_id=call.message.chat.id,
                                     reply_markup = types.ForceReply(selective = False),
                                     text="What are you searching for?")
                Bot.bot.register_next_step_handler(call.message, Bot.process_changes_fin)
        else:
            request.change = False

    # Handlers for main keyboard's buttons
    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        """Go back to the home page from search"""

        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.markup_home,
                                  text="Hello")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        """Permit user to change some parameters of request"""

        Bot.bot.send_message(chat_id = call.message.chat.id, text="Your settings: ")
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(Settings.SETTINGS),
                                  text="Tap on the setting you'd like to change")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        markup = types.InlineKeyboardMarkup()
        markup.row(*Settings.last_row)
        Bot.bot.send_message(chat_id=call.message.chat.id,
                             reply_markup=types.ForceReply(selective=False),
                             text="What are you searching for?")
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Result")
    def process_result(call):
        pass

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Help")
    def process_help(call):
        pass

    # Create new request
    @error_handler
    @restart_handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bunch(keywords=None, sort=None, sellers=None, solds=None,
                        rating=None, progress=0, change=None)
        Bot.request_dict[chat_id] = request
        request.keywords = message.text
        Bot.bot.reply_to(message, reply_markup=generate_markup(Settings.SORT_ORDERS),
                         text="Please, choose the sort order")

    # @error_handler
    # @bot.callback_query_handler(func=lambda call: call.data in Settings.SORT_ORDERS)
    # def process_sort(call):
    #     chat_id = call.message.chat.id
    #     request = Bot.request_dict[chat_id]
    #     request.sort = call.message.text
    #     Bot.changes_detector(call, request, "Please, choose the sort order(sellers)",
    #                          generate_markup(Settings.SELLERS_SORT_ORDERS))

    @error_handler
    #@bot.callback_query_handler(func=lambda call: call.data in Settings.SELLERS_SORT_ORDERS)
    @bot.callback_query_handler(func=lambda call: call.data in Settings.SORT_ORDERS)
    def process_sellers_sort(call):
        request = Bot.request_dict[call.message.chat.id]
        request.sellers = call.message.text
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in [90, 95, 99, 100, None]:
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data="rating " + str(i)))
        markup.row(*buttons)
        Bot.changes_detector(call, request, "How high should be seller's score? ", markup)

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
        Bot.changes_detector(call, request, "How high should be number of seller's sold items", markup)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data[:5] == 'solds')
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.solds = call.data[6:]
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in [1, 2, 3, 4, 5, 6, 7, 8]:
            buttons.append(types.InlineKeyboardButton(text=str(i), callback_data="progress" + str(i)))
        markup.row(*buttons)
        if not request.change:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup = markup,
                                      text="How many items do you want to see? Please, enter a number")
        Bot.bot.register_next_step_handler(call.message, Bot.process_num)

    @error_handler
    @restart_handler
    @bot.callback_query_handler(func=lambda call: call.data[:8] == 'progress')
    def process_num(call):
        request = Bot.request_dict[call.message.chat.id]
        request.num = int(call.data[8:])
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.progress_button,
                                  text="Please, wait...")
        Bot.send_results(call.message, request)

    @error_handler
    @restart_handler
    def process_changes_fin(message):
        request = Bot.request_dict[message.chat.id]
        request.keywords = message.text
        Bot.send_results(message, request)

    @error_handler
    @restart_handler
    def send_results(message, request):
        request.progress = 0
        helper = EbayApiHelper(request.keywords, request)
        futures = helper.futures(Settings.PAGES)
        xmldocs = []
        for i in futures:
            xmldocs.append(minidom.parse(i.result()))
        parser = ResponseParser(xmldocs, request.sellers, request.rating, request.solds)
        result = parser.parse_request()
        items = result
        for item in items[:request.num]:
            Bot.bot.send_message(message.chat.id, item)

    @error_handler
    @bot.callback_query_handler(func=lambda call: True)
    def process_change_settings(call):
        """Get the name of parameter user'd like to change"""


        chat_id = call.message.chat.id
        request = Bot.request_dict.get(chat_id)
        if not request:
            request = Bunch(keywords=None, sort=None, sellers=None,
                            solds=None, rating=None, progress=0,
                            change=None, num=Settings.NUM)
            Bot.request_dict[chat_id] = request
        change = call.data
        request.change = True
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=generate_markup(Settings.MARKUPS[change]),
                                  text="Tap")
    @classmethod
    def changes_detector(cls, call, request, text, markup):
        if not request.change:
            cls.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup,
                                      text=text)
        else:
            cls.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=generate_markup(Settings.CHANGES),
                                      text="What do you want to do?")

if __name__ == '__main__':
    random.seed()
    Bot = Bot()
    Bot.bot.remove_webhook()
    Bot.bot.polling(none_stop=True)