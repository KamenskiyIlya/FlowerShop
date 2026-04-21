"""
Клавиатуры действий с букетом.
Показывается под карточкой букета.
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_bouquet_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с действиями для текущего букета.
    
    Кнопки:
    - Заказать букет (переход к оформлению заказа)
    - Заказать консультацию (связь с флористом)
    - Посмотреть всю коллекцию (листание каталога)
    """
    keyboard = InlineKeyboardMarkup()
    
    # Основная кнопка действия
    keyboard.add(InlineKeyboardButton("Заказать букет", callback_data="action:order"))
    
    # Дополнительные опции (в одну строку)
    keyboard.add(
        InlineKeyboardButton("Заказать консультацию", callback_data="action:consult"),
        InlineKeyboardButton("Посмотреть всю коллекцию", callback_data="action:catalog")
    )
    
    return keyboard


def get_catalog_navigation_keyboard(current_index: int, total: int) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру навигации по каталогу.
    
    Args:
        current_index: текущий индекс букета в списке
        total: общее количество букетов
    
    Кнопки:
    - ← Назад (если не первый)
    - → Далее (если не последний)
    - Заказать этот букет
    """
    keyboard = InlineKeyboardMarkup()
    
    nav_buttons = []
    
    # Кнопка "Назад" (если есть предыдущий букет)
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("← Назад", callback_data=f"nav:prev:{current_index}"))
    
    # Кнопка "Далее" (если есть следующий букет)
    if current_index < total - 1:
        nav_buttons.append(InlineKeyboardButton("Далее →", callback_data=f"nav:next:{current_index}"))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    # Кнопка заказа текущего букета
    keyboard.add(InlineKeyboardButton("Заказать этот букет", callback_data="action:order"))
    
    return keyboard