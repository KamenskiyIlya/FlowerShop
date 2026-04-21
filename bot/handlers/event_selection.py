from telebot import TeleBot
from telebot.types import CallbackQuery, Message
from keyboards.budgets import get_budget_keyboard

# Глобальное хранилище сессий
user_data = {}

def register_event_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("event:"))
    def handle_event(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        event_key = call.data.split(":")[1]
        
        # Безопасная инициализация
        if call.message.chat.id not in user_data:
            user_data[call.message.chat.id] = {}
            
        if event_key == "other":
            msg = bot.send_message(call.message.chat.id, "Напишите, какой у вас повод:")
            bot.register_next_step_handler(msg, save_custom_event)
        else:
            user_data[call.message.chat.id]["event"] = event_key
            ask_budget(call.message)

    def save_custom_event(message: Message):
        if message.chat.id not in user_data:
            user_data[message.chat.id] = {}
        user_data[message.chat.id]["event"] = message.text.strip()
        ask_budget(message)

    def ask_budget(message: Message):
        bot.send_message(message.chat.id, "На какую сумму рассчитываете?", reply_markup=get_budget_keyboard())