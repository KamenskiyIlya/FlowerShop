# bot/handlers/budget_selection.py
"""
Обработчик выбора бюджета.
Подбирает букет и передаёт управление на показ карточки.
"""
from telebot import TeleBot
from telebot.types import CallbackQuery
from services.bouquet_service import get_bouquet_by_filters
from handlers.bouquet_show import show_bouquet_card
from handlers.event_selection import user_data
from keyboards.common import get_main_menu_inline_keyboard
from handlers.catalog import catalog_index, show_bouquet_with_nav

def register_budget_handler(bot: TeleBot):
    """Регистрирует обработчики выбора бюджета"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("budget:"))
    def handle_budget_selection(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        
        budget_value = call.data.split(":")[1]
        chat_id = call.message.chat.id
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        
        user_data[chat_id]["budget"] = budget_value
        event = user_data[chat_id].get("event")
        
        # НОВОЕ: получаем СПИСОК подходящих букетов
        from services.bouquet_service import get_bouquets_list_by_filters
        bouquets = get_bouquets_list_by_filters(event=event, budget=budget_value)
        
        if not bouquets:
            bot.send_message(
                chat_id,
                "Подходящих букетов не нашлось.\n\n"
                "Попробуйте изменить критерии или закажите консультацию флориста.",
                reply_markup=get_main_menu_inline_keyboard(),
            )
            return
        
        catalog_index[chat_id] = {
            'bouquets': bouquets,
            'index': 0,
            'is_filtered': True  # Флаг, что это подборка по фильтрам
        }
        
        # Показываем первый букет из списка с кнопками навигации
        show_bouquet_with_nav(bot, call.message, chat_id, 0, is_filtered=True)
