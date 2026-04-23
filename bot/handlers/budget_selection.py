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

def register_budget_handler(bot: TeleBot):
    """Регистрирует обработчики выбора бюджета"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("budget:"))
    def handle_budget_selection(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        
        # Извлекаем значение бюджета: "budget:1000" -> "1000"
        budget_value = call.data.split(":")[1]
        user_data[call.message.chat.id]["budget"] = budget_value
        
        event = user_data[call.message.chat.id].get("event")
        budget = budget_value
        
        # Подбор букета из БД
        bouquet = get_bouquet_by_filters(event=event, budget=budget)
        
        if bouquet:
            show_bouquet_card(bot, call.message, bouquet)
        else:
            bot.send_message(
                call.message.chat.id,
                "Подходящих букетов не нашлось.\n\n"
                "Попробуйте изменить критерии или закажите консультацию флориста.",
                reply_markup=get_main_menu_inline_keyboard(),
            )
