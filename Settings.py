from telebot import types
from Utils import generate_inline_button, generate_num_keyboard
SORT_ORDERS = ['Best Match', 'Price Plus Shipping Lowest', 'None']
SELLERS_SORT_ORDERS = ['Rating', 'Feedback Score', 'None']
SETTINGS = ['Keywords', 'Sort', 'Feedback', 'Rating']
CHANGES = ['Get results', 'Change another one setting', 'Accept changes']
MARKUPS = {'Sort': SORT_ORDERS}
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

RATING = generate_num_keyboard(0, 100, "rating", next=1)