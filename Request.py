import Settings
import Utils
from Utils import bot
from EbayApiHelper import EbayApiHelper
from ResponseParser import ResponseParser
from io import BytesIO
from xml.dom import minidom

class Request:
    def __init__(self):
        self.keywords = None
        self.sort = None
        self.feedback = 0
        self.rating = 0
        self.change = False
        self.markups = {Settings.LABELS['Rating']: Settings.RATING}
        self.page = 0
        self.pages = None
        self.message = None
        self.items = []

    def change_num_keyword(self, label, call):
        self.markups[label] = Utils.change_markup(self.markups[label], call.data, label)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=self.markups[label])

    def changes_detector(self, call, text, markup):
        if not self.change:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=markup,
                                  text=text)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=Settings.MARKUPS['Changes'],
                                  text="What do you want to do?")
    def get_result(self):
        bot.edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id,
                                  text="Please, wait...\n0% is done")

        helper = EbayApiHelper(self.keywords, self.sort, self.message)
        futures = helper.futures(Settings.PAGES)
        xmldocs = []
        for i in futures:
            xmldocs.append(minidom.parse(BytesIO(i.result())))
        parser = ResponseParser(xmldocs, self.rating, self.feedback)
        self.items = parser.items
        bot.edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id,
                                  text="DONE")
        self.send_result()

    def send_result(self):
        if not self.items:
            bot.edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id,
                                      reply_markup=Settings.markup_home,
                                      text="No items were found. Please, try another request")
            return
        markup = Utils.generate_next_prev_keyboard(0, round(len(self.items) / 4))
        items_split = [self.items[i:i + 4] for i in range(0, len(self.items), 4)]
        pages = list(map(Utils.make_page, items_split))
        self.pages = pages
        self.page = 0
        bot.edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id, text=pages[0],
                                  parse_mode='html', disable_web_page_preview=True, reply_markup=markup)