from telebot import types
from Utils import generate_inline_button, generate_num_keyboard, generate_markup
SORT_ORDERS = ['Best Match', 'Price Plus Shipping Lowest', 'None']
SELLERS_SORT_ORDERS = ['Rating', 'Feedback Score', 'None']
SETTINGS = ['Keywords', 'Sort', 'Feedback', 'Rating']
CHANGES = ['Get results', 'Change another one setting', 'Accept changes']
LABELS = {'Rating': 'rating ', 'Num': 'num ', 'Feedback': 'feedback '}
PAGES = 100
NUM = 10  # default number of items in result

markup_home = types.InlineKeyboardMarkup()
markup_home.row(generate_inline_button("Search"))
markup_home.row(generate_inline_button("Result"))
markup_home.row(generate_inline_button("Help"),
                generate_inline_button("Settings"))

last_row = generate_inline_button("Main Menu"), \
           generate_inline_button("Help")

progress_button = types.InlineKeyboardMarkup()
progress_button.row(generate_inline_button("Get progress"))

FEEDBACK = types.InlineKeyboardMarkup()
buttons = []
for i in [100, 1000, 10000, None]:
    buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=LABELS["Feedback"] + str(i)))
FEEDBACK.row(*buttons)
FEEDBACK.row(*last_row)

RATING = generate_num_keyboard(0, 100, LABELS["Rating"], next=1)
NUM_KEYBOARD = generate_num_keyboard(1, 20,  LABELS["Num"], next=2)

MARKUPS = {'Sort': generate_markup(SORT_ORDERS), 'Settings': generate_markup(SETTINGS),
           'Feedback': FEEDBACK, 'Num': NUM_KEYBOARD, 'Rating': RATING}