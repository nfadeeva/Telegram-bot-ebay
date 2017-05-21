import Utils
from Utils import error_handler, restart_handler
from Request import Request
import Settings
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
import random
import telebot
from xml.dom import minidom


class Bot:
    request_dict = {}
    bot = Utils.bot

    # Main commands

    # !
    @error_handler
    @bot.message_handler(commands=['start'])
    def start(message):
        Bot.bot.send_message(message.chat.id, reply_markup=Settings.markup_home,
                             text="Hello \U0001f604")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in Settings.CHANGES)
    def process_next_changes(call):
        """What bot should to do after changing settings"""

        request = Bot.request_dict[call.message.chat.id]
        request.change = False
        if call.data == 'Change another one setting':
            request.change = True
            Utils.functions[call.data](call)
        elif call.data == 'Get results':
            if request.keywords:
                Bot.send_results(call.message, request)
            else:
                Utils.functions["Search"](call)
                Bot.bot.register_next_step_handler(call.message, Bot.process_changes_fin)

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

        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.MARKUPS['Settings'],
                                  text="Tap on the setting you'd like to change")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Utils.functions["Search"](call)
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
        request = Bot.request_dict.get(chat_id)
        if request and request.change:
            request.keywords = message.text
            Bot.bot.send_message(chat_id=message.chat.id,
                                 reply_markup=Settings.MARKUPS["Changes"],
                                 text="What do you want to do?")
        else:
            request = Request(chat_id=chat_id)
            Bot.request_dict[chat_id] = request
            request.keywords = message.text
            Bot.bot.reply_to(message, reply_markup=Settings.MARKUPS['Sort'],
                         text="Please, choose the sort order")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in Settings.SORT_ORDERS)
    def process_sellers_sort(call):
        request = Bot.request_dict[call.message.chat.id]
        request.sellers = call.message.text
        request.changes_detector(call, "How high should be seller's rating? ", Settings.RATING)

    @error_handler
    @bot.callback_query_handler(func=lambda call: Settings.LABELS['Rating'] in call.data)
    def process_sellers_rating(call):
        request = Bot.request_dict[call.message.chat.id]
        if "keyboard" in call.data:
            request.change_num_keyword(Settings.LABELS['Rating'], call)
        else:
            request.rating = call.data.split()[1]
            request.changes_detector(call, "How high should be number of seller's feedback?",
                                   Settings.MARKUPS['Feedback'])

    @error_handler
    @bot.callback_query_handler(func=lambda call: Settings.LABELS['Feedback'] in call.data)
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.feedback = call.data.split()[1]
        request.changes_detector(call, "How many items do you want to see?",
                                   Settings.MARKUPS['Num'])

    @error_handler
    @restart_handler
    @bot.callback_query_handler(func=lambda call: Settings.LABELS['Num'] in call.data)
    def process_num(call):
        request = Bot.request_dict[call.message.chat.id]
        if "keyboard" in call.data:
            request.change_num_keyword(Settings.LABELS['Num'], call)
        else:
            request.num = int(call.data.split()[1])
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
        Bot.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text="Please, wait...\n0% is done")
        request.progress = 0
        helper = EbayApiHelper(request.keywords, request, message)
        futures = helper.futures(Settings.PAGES)
        xmldocs = []
        for i in futures:
            xmldocs.append(minidom.parse(i.result()))
        parser = ResponseParser(xmldocs, request.sellers, request.rating, request.feedback)
        items = parser.parse_request()
        Bot.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text="DONE")
        for item in items[:request.num]:
            Bot.bot.send_message(message.chat.id, item)
        Bot.bot.send_message(message.chat.id, reply_markup=Settings.markup_home,
                             text="Hello \U0001f604")

    @error_handler
    @bot.callback_query_handler(func=lambda call: True)
    def process_change_settings(call):
        """Get the name of parameter user'd like to change"""

        chat_id = call.message.chat.id
        request = Bot.request_dict.get(chat_id)
        if not request:
            request = Request(chat_id=chat_id)
            Bot.request_dict[chat_id] = request
        change = call.data
        request.change = True
        markup = Settings.MARKUPS.get(change)
        if markup:
            Bot.bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  reply_markup=markup,
                                  text="Change setting")
        else:
            Utils.functions["Search"](call)
            Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)


if __name__ == '__main__':
    random.seed()
    Bot = Bot()
    Bot.bot.remove_webhook()
    Bot.bot.polling(none_stop=True)