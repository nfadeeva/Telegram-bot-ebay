from telebot import types
from Utils import generate_inline_button, generate_num_keyboard, generate_markup
SORT_ORDERS = ['Best Match', 'Price Plus Shipping Lowest', 'None']
SETTINGS = ['Keywords', 'Sort', 'Feedback', 'Rating']
CHANGES = ['Get results', 'Change another one setting', 'Accept changes']
LABELS = {'Rating': 'rating ', 'Num': 'num ', 'Feedback': 'feedback '}
PAGES = 60
NUM = 10  # default number of items in result

markup_home = types.InlineKeyboardMarkup()
markup_home.row(generate_inline_button("Search"))
markup_home.row(generate_inline_button("Help"),
                generate_inline_button("Settings"))

last_row = generate_inline_button("Main Menu"), \
           generate_inline_button("Help")

FEEDBACK = types.InlineKeyboardMarkup()
buttons = []
for i in [(100,"Low (>=100)"),  (1000," Medium (>=1000)"), (10000, "High (>=10000)"),
          (500000, "Very high(>=500000)"), (0, "Don't Care")]:
    buttons.append(types.InlineKeyboardButton(text=str(i[1]),
                                              callback_data=LABELS["Feedback"] + str(i[0])))
FEEDBACK.row(*buttons[:2])
FEEDBACK.row(*buttons[2:-2])
FEEDBACK.row(buttons[-2])
FEEDBACK.row(buttons[-1])
FEEDBACK.row(*last_row)

RATING = generate_num_keyboard(0, 100, LABELS["Rating"], next=1)
NUM_KEYBOARD = generate_num_keyboard(1, 20,  LABELS["Num"], next=2)

MARKUPS = {'Sort': generate_markup(SORT_ORDERS), 'Settings': generate_markup(SETTINGS),
           'Feedback': FEEDBACK, 'Num': NUM_KEYBOARD, 'Rating': RATING,
           'Changes': generate_markup(CHANGES)}