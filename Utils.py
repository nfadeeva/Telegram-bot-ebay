import config
import telebot
from telebot import types
import functools

bot = telebot.TeleBot(config.token)

EMODJI = {"Search": "\U0001F50E",
          "Main Menu": "\U0001F3E0",
          "Settings": "\U0001F527",
          "Result": "\U0001F6CD",
          "Help": "\U00002753",
          "Item": "\U0001F535"
          }

PAGES = 50

SETTINGS = ['Keywords', 'Sort', 'Feedback Rating', 'Positive Ratings Percentage']
CHANGES = ['Get results', 'Change another one setting', 'Accept changes']
SORT_ORDERS = ['Best Match', 'Price Plus Shipping Lowest', 'None']
LABELS = {'Rating': 'rating ','Feedback': 'feedback '}

HELP_TEXT = "You can get the list of items from eBay filtered by specific way!\n\n" \
            "In private chat you can see items from result of your request.\n" \
            "Just type @EbayItemsBot and any text, " \
            "press enter and see items from your last request"

FUNCTIONS = {"Change another one setting": lambda call:
              bot.edit_message_text(chat_id=call.message.chat.id,
                  message_id=call.message.message_id,
                  reply_markup=generate_markup(SETTINGS),
                  text="Tap on the setting you'd like to change"),
             "Search": lambda call:
              bot.send_message(chat_id=call.message.chat.id,
                                  reply_markup=types.ForceReply(selective=False),
                                  text="What are you searching for?"),
             "Change": lambda call:
             bot.edit_message_text(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   reply_markup=generate_markup(CHANGES),
                                   text="What do you want to do?")
             }


def restart_handler(func):
    """Fix issue with multiple dialogs"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if args start with '__main__.Bot' or __message
        index = 0
        try:
            message = args[0]
            text = message.text
        except:
            index = 1
            message = args[1]
            text = message.text
        # So nothing because another one bot will handle '/start'
        if text == '/start':
            return
        return func(*args[index:], **kwargs)
    return wrapper


def generate_inline_button(label):
    return types.InlineKeyboardButton(text=label + " " + EMODJI[label],
                                      callback_data=label)

LAST_ROW = generate_inline_button("Main Menu")


def generate_markup(items):
    markup = None
    if items:
        markup = types.InlineKeyboardMarkup()
        for i in items:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
        markup.row(LAST_ROW)
    return markup


def generate_next_prev_keyboard(cur, end):
    markup = types.InlineKeyboardMarkup()
    next_btn = types.InlineKeyboardButton(text="Next Page »",
                               callback_data="Next " + str(cur))
    prev_btn = types.InlineKeyboardButton(text="« Previous Page",
                               callback_data="Prev " + str(cur))
    if cur == 0:
        markup.add(next_btn)
    elif cur == end - 1:
        markup.add(prev_btn)
    else:
        markup.row(prev_btn, next_btn)
    markup.row(LAST_ROW)
    return markup


def make_page(items):
    text = ''
    for item in items:
        text += r'''<a href="{}">{}</a>'''.format(item.url, item.title + "...") + \
                "\n<b>Feedback Rating: </b>{} points\n" \
                "<b>Positive feedbacks: </b>{}%\n" \
                "<b>Price: </b>{}$\n<b>" \
                "Shipping: </b>{}$\n".format(item.feedback, item.rating, item.price, item.shipping) + "\n"
    return text


def generate_num_keyboard(start, end, text, type=None, next=None):
    markup = types.InlineKeyboardMarkup()
    label = text + "keyboard"
    buttons = []
    first_button = types.InlineKeyboardButton(text="« " + str(start),
                                              callback_data=label + str(start) + "«")
    last_button = types.InlineKeyboardButton(text=str(end) + " »",
                                             callback_data=label + str(end)+"»")
    if type == "Left":
        for i in range(start, start + 3):
            buttons.append(types.InlineKeyboardButton(text=str(i),
                                                      callback_data=text + str(i)))
        buttons.append(types.InlineKeyboardButton(text=str(start + 3) + " ›",
                                                  callback_data=label + str(start + 3)))
        buttons.append(last_button)
    elif type == "Right":
        buttons.append(first_button)
        buttons.append(types.InlineKeyboardButton(text="‹ " + str(end - 3),
                                                  callback_data=label + str(end - 3) + "‹"))
        for i in range(end - 2, end + 1):
            buttons.append(types.InlineKeyboardButton(text=str(i),
                                                      callback_data=text + str(i)))
    else:
        buttons.append(first_button)
        buttons.append(types.InlineKeyboardButton(text="‹ "+str(next),
                                                  callback_data=label + "‹"+str(next)))
        buttons.append(types.InlineKeyboardButton(text=str(next+1),
                                                  callback_data=text + str(next+1)))
        buttons.append(types.InlineKeyboardButton(text=str(next+2) + " ›",
                                                  callback_data=label + str(next+2) + "›"))
        buttons.append(last_button)

    markup.row(*buttons)
    markup.row(LAST_ROW)
    return markup


def change_markup(markup, data, text):
    markups_dict = markup.to_dic()['inline_keyboard'][0]
    nums = list(map(lambda x: int(x['text'].strip("«‹›»")), markups_dict))
    start, end = nums[0], nums[-1]
    type, next = None, None
    if "«" in data:
        type = "Left"
    elif "»" in data:
        type = "Right"
    elif "‹" in data:
        if not nums[1] == start + 1:
            next = nums[1] - 1
        else:
            type = "Left"
    else:
        if not nums[-2] == end - 1:
            next = nums[1] + 1
        else:
            type = "Right"
    return generate_num_keyboard(start, end, text, type=type, next=next)


def markup_feedback():
    markup_feedback = types.InlineKeyboardMarkup()
    buttons = []
    for i in [(100,"Low (>=100)"),  (1000," Medium (>=1000)"), (10000, "High (>=10000)"),
              (500000, "Very high(>=500000)"), (0, "Don't Care")]:
        buttons.append(types.InlineKeyboardButton(text=str(i[1]),
                                                  callback_data=LABELS["Feedback"] + str(i[0])))
    markup_feedback.row(*buttons[:2])
    markup_feedback.row(*buttons[2:-2])
    markup_feedback.row(buttons[-2])
    markup_feedback.row(buttons[-1])
    markup_feedback.row(LAST_ROW)
    return markup_feedback


def markup_home():
    markup_home = types.InlineKeyboardMarkup()
    markup_home.row(generate_inline_button("Search"))
    markup_home.row(generate_inline_button("Result"))
    markup_home.row(generate_inline_button("Settings"))
    return markup_home

MARKUPS = {'Sort': generate_markup(SORT_ORDERS), 'Settings': generate_markup(SETTINGS),
           'Feedback Rating': markup_feedback(),
           'Positive Ratings Percentage': generate_num_keyboard(0, 100, LABELS["Rating"], next=1),
           'Changes': generate_markup(CHANGES), 'Home': markup_home(), 'Last': types.InlineKeyboardMarkup().row(LAST_ROW)}