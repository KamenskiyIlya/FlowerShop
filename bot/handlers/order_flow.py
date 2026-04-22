# handlers/order_flow.py
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handlers.event_selection import user_data
from services.order_service import create_order_from_bot_payload
from services.notification_service import notify_courier_about_order

# Множество для отслеживания уже обработанных заказов
_processing_chats = set()

def register_order_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "action:order")
    def start_order(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        if "current_bouquet_id" not in user_data[chat_id]:
            bot.send_message(chat_id, "Сначала выберите букет")
            return
            
        msg = bot.send_message(chat_id, "Введите ваше имя:")
        bot.register_next_step_handler(msg, collect_name)

    def collect_name(message: Message):
        if message.chat.id not in user_data: user_data[message.chat.id] = {}
        user_data[message.chat.id]["client_name"] = message.text.strip()
        msg = bot.send_message(message.chat.id, "Укажите адрес доставки:")
        bot.register_next_step_handler(msg, collect_address)

    def collect_address(message: Message):
        if message.chat.id not in user_data: user_data[message.chat.id] = {}
        user_data[message.chat.id]["address"] = message.text.strip()
        msg = bot.send_message(message.chat.id, "Укажите дату и время доставки (например: 15.05 в 14:00):")
        bot.register_next_step_handler(msg, collect_datetime)

    def collect_datetime(message: Message):
        chat_id = message.chat.id
        
        # Защита от повторного срабатывания
        if chat_id in _processing_chats:
            return
        _processing_chats.add(chat_id)
        
        if chat_id not in user_data: user_data[chat_id] = {}
        user_data[chat_id]["datetime"] = message.text.strip()

        payload = {
            "telegram_id": chat_id,
            "username": message.from_user.username if message.from_user else "",
            "bouquet_id": user_data[chat_id].get("current_bouquet_id"),
            "client_name": user_data[chat_id].get("client_name"),
            "address": user_data[chat_id].get("address"),
            "datetime": user_data[chat_id].get("datetime"),
            "phone": user_data[chat_id].get("phone"),
        }

        order = create_order_from_bot_payload(payload)
        notify_courier_about_order(bot, order_data=order, payload=payload)
        bot.send_message(
            chat_id,
            f"Заказ принят! Номер заказа: #{order['order_number']}.\n"
            f"Курьер свяжется с вами для уточнения деталей."
        )
        
        # Очистка
        user_data.pop(chat_id, None)
        _processing_chats.discard(chat_id)
