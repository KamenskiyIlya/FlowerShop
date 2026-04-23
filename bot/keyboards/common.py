from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_TEXT = "В главное меню"
MAIN_MENU_CALLBACK = "menu:main"


def get_main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(MAIN_MENU_TEXT, callback_data=MAIN_MENU_CALLBACK))
    return keyboard


def get_main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton(MAIN_MENU_TEXT))
    return keyboard
