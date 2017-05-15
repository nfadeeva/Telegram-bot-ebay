from telebot import types
from Utils import generate_inline_button
SORT_ORDERS = ['BestMatch', 'PricePlusShippingLowest', 'None']
SELLERS_SORT_ORDERS = ['Rating', 'FeedbackScore', 'None']
SETTINGS = ['Keywords', 'Sort', 'Sellers', 'Solds', 'Rating']
CHANGES = ['Get results', 'Change another one setting', 'Accept CHANGES']
MARKUPS = {'Sort': SORT_ORDERS, 'Sellers': SELLERS_SORT_ORDERS}
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
progress_button.row(generate_inline_button("Progress"))