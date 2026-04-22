# handlers/consultation_flow.py
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handlers.event_selection import user_data
from services.notification_service import notify_florist_about_consultation

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
        consultation_data = {
            "telegram_id": chat_id,
            "client_name": message.from_user.first_name if message.from_user else "",
            "phone": user_data[chat_id].get("phone"),
            "event": user_data[chat_id].get("event"),
            "budget": user_data[chat_id].get("budget"),
            "bouquet_id": user_data[chat_id].get("current_bouquet_id"),
        }
        notify_florist_about_consultation(bot, consultation_data=consultation_data)
        bot.send_message(chat_id, "Флорист скоро свяжется с вами. А пока можете присмотреть что-нибудь из коллекции.")
        
        # Очищаем только телефон, оставляя повод/бюджет для следующих шагов
        user_data[chat_id].pop("phone", None)
