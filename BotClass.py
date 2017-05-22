import Utils
from Utils import error_handler, restart_handler
from Request import Request
import time
import Settings

import random
from telebot import types



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
                Bot.send_result(call.message, request)
            else:
                Utils.functions["Search"](call)
                Bot.bot.register_next_step_handler(call.message, Bot.process_changes_fin)
        else:
            Bot.load_main_menu(call)

    # Handlers for main keyboard's buttons
    @staticmethod
    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        """Go back to the home page from search"""

        request = Bot.request_dict.get(call.message.chat.id)
        if request:
            request.change = False
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.markup_home,
                                  text="Hello")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Result")
    def process_settings(call):
        """Permit user to change some parameters of request"""
        request = Bot.request_dict.get(call.message.chat.id)
        if request and request.pages:
            markup = Utils.generate_next_prev_keyboard(request.page, round(len(request.pages) / 4))
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=request.pages[request.page], parse_mode='html',
                                      disable_web_page_preview=True, reply_markup=markup)
        else:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="There is nothing to show, please, make request and see result here",
                                      disable_web_page_preview=True, reply_markup=Settings.markup_last)

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        """Permit user to change some parameters of request"""
        request = Bot.request_dict.get(call.message.chat.id, Request())
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Settings.MARKUPS['Settings'],
                                  text="<b>Keywords:</b> {}\n"
                                       "<b>Sort:</b> {}\n"
                                       "<b>Positive feedback:</b> {}%\n"
                                       "<b>Rating:</b>{} points\n\nPlease, choose the option you'd like to change"
                                       .format(request.keywords, request.sort, request.rating, request.feedback),
                                  parse_mode='html')

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Utils.functions["Search"](call)
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

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
            request = Request()
            Bot.request_dict[chat_id] = request
            request.keywords = message.text
            Bot.bot.reply_to(message, reply_markup=Settings.MARKUPS['Sort'],
                         text="Please, choose the sort order")

    @error_handler
    @bot.callback_query_handler(func=lambda call: call.data in Settings.SORT_ORDERS)
    def process_sellers_sort(call):
        request = Bot.request_dict[call.message.chat.id]
        request.sort = call.data
        request.changes_detector(call, "How high should be seller's positive ratings percentage? ", Settings.RATING)

    @error_handler
    @bot.callback_query_handler(func=lambda call: Settings.LABELS['Rating'] in call.data)
    def process_sellers_rating(call):
        request = Bot.request_dict[call.message.chat.id]
        if "keyboard" in call.data:
            request.change_num_keyword(Settings.LABELS['Rating'], call)
        else:
            request.rating = call.data.split()[1]
            request.changes_detector(call, "How high should be seller's feedback rating?",
                                   Settings.MARKUPS['Feedback'])

    @error_handler
    @bot.callback_query_handler(func=lambda call: Settings.LABELS['Feedback'] in call.data)
    def process_sellers_rating(call):
        chat_id = call.message.chat.id
        request = Bot.request_dict[chat_id]
        request.feedback = call.data.split()[1]
        Bot.send_result(call.message, request)

    @error_handler
    @restart_handler
    def process_changes_fin(message):
        request = Bot.request_dict[message.chat.id]
        request.keywords = message.text
        request.message = message
        request.get_result()


    @error_handler
    @restart_handler
    @bot.callback_query_handler(func=lambda call: "Next" in call.data or "Prev" in call.data)
    def process_change(call):
        label, cur = call.data.split()
        cur = int(cur)
        request = Bot.request_dict[call.message.chat.id]
        markup = None
        if label == "Next":
            request.page += 1
            markup = Utils.generate_next_prev_keyboard(cur + 1, len(request.pages))
        if label == "Prev":
            request.page -= 1
            markup = Utils.generate_next_prev_keyboard(cur - 1, len(request.pages))
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=request.pages[cur], parse_mode='html',
                                  disable_web_page_preview=True, reply_markup=markup)

    @error_handler
    @bot.callback_query_handler(func=lambda call: True)
    def process_change_settings(call):
        """Get the name of parameter user'd like to change"""

        request = Bot.request_dict.get(call.message.chat.id, Request())
        Bot.request_dict[call.message.chat.id] = request
        change = call.data
        request.change = True
        markup = Settings.MARKUPS.get(change)
        if markup:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup,
                                      text="Please, change {}".format(change))
        else:
            Utils.functions["Search"](call)
            Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @bot.inline_handler(lambda query: True)
    def query_text(query):
        request = Bot.request_dict.get(query.from_user.id, Request())
        articles = []
        for item in request.items[:30]:
            articles.append(types.InlineQueryResultArticle(
                id=str(request.items.index(item)), title=item.title,
                description="{} USD Shipping: {} USD".format(item.price,item.shipping),
                input_message_content=types.InputTextMessageContent(
                    message_text=Utils.make_page([item]), parse_mode='html'),
                url=item.url, thumb_url=item.img, thumb_height=48, thumb_width=48
            ))
        Bot.bot.answer_inline_query(query.id, articles)

if __name__ == '__main__':
    random.seed()
    Bot = Bot()
    Bot.bot.remove_webhook()
    Bot.bot.polling(none_stop=True)