from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_catalog_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Назад", callback_data="nav:prev"),
        InlineKeyboardButton("Вперед", callback_data="nav:next"),
    )
    kb.add(InlineKeyboardButton("Главное меню", callback_data="nav:main"))
    return kb