"""
Клавиатуры для выбора повода (события).
Используется на первом шаге после приветствия.
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_events_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопками выбора повода.
    
    Кнопки:
    - День рождения
    - Свадьба
    - В школу
    - Без повода
    - Другой повод (открывает подменю для ввода текста)
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Добавляем кнопки с callback_data для обработки
    keyboard.add(
        InlineKeyboardButton("День рождения", callback_data="event:birthday"),
        InlineKeyboardButton("Свадьба", callback_data="event:wedding"),
        InlineKeyboardButton("В школу", callback_data="event:school"),
        InlineKeyboardButton("Без повода", callback_data="event:none"),
        InlineKeyboardButton("Другой повод", callback_data="event:other")
    )
    
    return keyboard