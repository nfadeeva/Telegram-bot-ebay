from telebot import types
from Utils import generate_inline_button, generate_num_keyboard, generate_markup
SORT_ORDERS = ['Best Match', 'Price Plus Shipping Lowest', 'None']
SETTINGS = ['Keywords', 'Sort', 'Feedback Rating', 'Positive Ratings Percentage']
CHANGES = ['Get results', 'Change another one setting', 'Accept changes']
LABELS = {'Rating': 'rating ','Feedback': 'feedback '}
PAGES = 50

markup_home = types.InlineKeyboardMarkup()
markup_home.row(generate_inline_button("Search"))
markup_home.row(generate_inline_button("Result"))
markup_home.row(generate_inline_button("Settings"))
markup_last = types.InlineKeyboardMarkup()
last_row = generate_inline_button("Main Menu")
markup_last.row(last_row)
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
FEEDBACK.row(last_row)

RATING = generate_num_keyboard(0, 100, LABELS["Rating"], next=1)

MARKUPS = {'Sort': generate_markup(SORT_ORDERS), 'Settings': generate_markup(SETTINGS),
           'Feedback Rating': FEEDBACK, 'Positive Ratings Percentage': RATING,
           'Changes': generate_markup(CHANGES)}