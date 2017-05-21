import Settings
import Utils
from Utils import bot


class Request:
    def __init__(self, chat_id):
        self.keywords = None
        self.sort = None
        self.feedback = None
        self.rating = None
        self.progress = 0
        self.change = False
        self.markups = {Settings.LABELS['Rating']: Settings.RATING,
                        Settings.LABELS['Num']: Settings.NUM_KEYBOARD}
        self.chat_id = chat_id
        self.updater = False

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
    def update_progress(self, message):
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                       text="Please, wait...\n"
                                        "{}% is done".format(self.progress))