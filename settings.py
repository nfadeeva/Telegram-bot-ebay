from telebot import types
from utils import generate_inline_button
sort_orders = ['BestMatch', 'PricePlusShippingLowest', 'None']
sellers_sort_orders = ['Rating', 'FeedbackScore','None']
settings = ['Keywords', 'Sort', 'Sellers', 'Solds', 'Rating']
changes = ['Get results', 'Change another one setting', 'Accept changes']
markups = {'Sort': sort_orders, 'Sellers': sellers_sort_orders}
pages = 100


markup_home = types.InlineKeyboardMarkup()
markup_home.row(generate_inline_button("Search"))
markup_home.row(generate_inline_button("Result"))
markup_home.row(generate_inline_button("Help"),
                generate_inline_button("Settings"))

last_row = generate_inline_button("Main Menu"), \
           generate_inline_button("Back"), \
           generate_inline_button("Help")