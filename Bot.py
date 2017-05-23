import Utils
from Utils import restart_handler
from Request import Request
import random
from telebot import types


class Bot:
    """Main bot to interact with user"""

    request_dict = {}
    bot = Utils.bot

    @bot.message_handler(commands=['start'])
    def start(message):
        Bot.bot.send_message(message.chat.id, reply_markup=Utils.MARKUPS['Home'],
                             text="Let's start!\n\n" + Utils.HELP_TEXT)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "Main Menu")
    def load_main_menu(call):
        request = Bot.request_dict.get(call.message.chat.id)
        if request:
            request.change = False
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Let's start!\n\n"+ Utils.HELP_TEXT,
                                  reply_markup=Utils.MARKUPS['Home'])

    @restart_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Result")
    def process_result(call):
        request = Bot.request_dict.get(call.message.chat.id)
        if request and request.pages:
            markup = Utils.generate_next_prev_keyboard(request.page, round(len(request.pages) / 4))
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=request.pages[request.page], parse_mode='html',
                                      disable_web_page_preview=True, reply_markup=markup)
        else:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="There is nothing to show, please, make request and see result here",
                                      disable_web_page_preview=True, reply_markup=Utils.MARKUPS['Home'])

    @restart_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Settings")
    def process_settings(call):
        """Permit user to change some parameters of request"""

        request = Bot.request_dict.get(call.message.chat.id, Request())
        Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=Utils.MARKUPS['Settings'],
                                  text="<b>Keywords:</b> {}\n"
                                       "<b>Sort:</b> {}\n"
                                       "<b>Positive feedback:</b> {}%\n"
                                       "<b>Rating:</b> {} points\n\nPlease, choose the option you'd like to change"
                                       .format(request.keywords, request.sort, request.rating, request.feedback),
                                  parse_mode='html')

    @restart_handler
    @bot.callback_query_handler(func=lambda call: call.data == "Search")
    def process_search(call):
        Utils.FUNCTIONS["Search"](call)
        Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @restart_handler
    def process_keywords(message):
        chat_id = message.chat.id
        request = Bot.request_dict.get(chat_id)
        if request and request.change:
            request.keywords = message.text
            Bot.bot.send_message(chat_id=message.chat.id,
                                 reply_markup=Utils.MARKUPS["Changes"],
                                 text="What do you want to do?")
        else:
            request = Request()
            Bot.request_dict[chat_id] = request
            request.keywords = message.text
            Bot.bot.reply_to(message, reply_markup=Utils.MARKUPS['Sort'],
                         text="Please, choose the sort order")

    @bot.callback_query_handler(func=lambda call: call.data in Utils.SORT_ORDERS)
    def process_sellers_sort(call):
        request = Bot.request_dict[call.message.chat.id]
        request.sort = call.data
        request.changes_detector(call, "How high should be seller's positive ratings percentage be? ",
                                 Utils.MARKUPS['Positive Ratings Percentage'])

    @bot.callback_query_handler(func=lambda call: Utils.LABELS['Rating'] in call.data)
    def process_sellers_rating(call):
        request = Bot.request_dict[call.message.chat.id]
        if "keyboard" in call.data:
            request.change_num_keyword(Utils.LABELS['Rating'], call)
        else:
            request.rating = call.data.split()[1]
            request.changes_detector(call, "How high should be seller's feedback rating be?",
                                    Utils.MARKUPS['Feedback Rating'])

    @restart_handler
    @bot.callback_query_handler(func=lambda call: call.data in Utils.CHANGES)
    def process_next_changes(call):
        """What bot should to do after changing settings"""

        request = Bot.request_dict[call.message.chat.id]
        request.change = False
        if call.data == 'Change another one setting':
            request.change = True
            Utils.FUNCTIONS[call.data](call)
        elif call.data == 'Get results':
            if request.keywords:
                request.message = call.message
                request.send_result()
            else:
                Utils.FUNCTIONS["Search"](call)
                Bot.bot.register_next_step_handler(call.message, Bot.process_changes_fin)
        else:
            Bot.load_main_menu(call)

    @bot.callback_query_handler(func=lambda call: Utils.LABELS['Feedback'] in call.data)
    def process_sellers_rating(call):
        request = Bot.request_dict[call.message.chat.id]
        request.feedback = call.data.split()[1]
        request.message = call.message

        if not request.change:
            request.send_result()
        else:
            Utils.FUNCTIONS["Change"](call)

    @restart_handler
    def process_changes_fin(message):
        request = Bot.request_dict[message.chat.id]
        request.keywords = message.text
        request.message = message
        request.send_result()

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

    @restart_handler
    @bot.callback_query_handler(func=lambda call: True)
    def process_change_settings(call):
        """Get the name of parameter user'd like to change"""

        request = Bot.request_dict.get(call.message.chat.id, Request())
        Bot.request_dict[call.message.chat.id] = request
        change = call.data
        request.change = True
        markup = Utils.MARKUPS.get(change)
        if markup:
            Bot.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup,
                                      text="Please, change {}".format(change))
        else:
            Utils.FUNCTIONS["Search"](call)
            Bot.bot.register_next_step_handler(call.message, Bot.process_keywords)

    @restart_handler
    @bot.inline_handler(lambda query: True)
    def inline_mode(query):
        request = Bot.request_dict.get(query.from_user.id, Request())
        articles = []
        for item in request.items[:30]:
            articles.append(types.InlineQueryResultArticle(
                id=str(request.items.index(item)), title=item.title,
                description="{} USD Shipping: {} USD".format(item.price, item.shipping),
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