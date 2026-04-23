from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_promo_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('Есть промокод', callback_data='promo:yes'),
        InlineKeyboardButton('Пропустить', callback_data='promo:no')
    )
    
    return keyboard