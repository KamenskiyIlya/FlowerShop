"""
Клавиатуры для выбора бюджета.
Показывается после выбора повода.
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_budget_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с вариантами бюджета.
    
    Варианты:
    - ~500 ₽
    - ~1000 ₽
    - ~2000 ₽
    - Больше
    - Не важно (показать любой букет)
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("~500 ₽", callback_data="budget:500"),
        InlineKeyboardButton("~1000 ₽", callback_data="budget:1000"),
        InlineKeyboardButton("~2000 ₽", callback_data="budget:2000"),
        InlineKeyboardButton("Больше", callback_data="budget:more"),
        InlineKeyboardButton("Не важно", callback_data="budget:any")
    )
    
    return keyboard