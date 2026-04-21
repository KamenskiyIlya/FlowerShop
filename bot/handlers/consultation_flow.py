# handlers/consultation_flow.py
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handlers.event_selection import user_data

def register_consultation_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "action:consult")
    def start_consult(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id, 
            "Укажите номер телефона, и флорист перезвонит в течение 20 минут:"
        )
        bot.register_next_step_handler(msg, collect_phone)

    def collect_phone(message: Message):
        chat_id = message.chat.id
        
        # Инициализируем, если сессия пуста
        if chat_id not in user_data:
            user_data[chat_id] = {}
            
        user_data[chat_id]["phone"] = message.text.strip()
        bot.send_message(chat_id, "Флорист скоро свяжется с вами. А пока можете присмотреть что-нибудь из коллекции.")
        
        # Очищаем только телефон, оставляя повод/бюджет для следующих шагов
        user_data[chat_id].pop("phone", None)