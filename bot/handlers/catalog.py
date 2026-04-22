# handlers/catalog.py
from telebot import TeleBot
from telebot.types import CallbackQuery
from handlers.event_selection import user_data
from services.bouquet_service import get_all_bouquets
from handlers.bouquet_show import show_bouquet_card
from random import choice

def register_catalog_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "action:catalog")
    def show_catalog(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        # Инициализируем сессию
        if chat_id not in user_data:
            user_data[chat_id] = {}

        bouquets = get_all_bouquets()
        if bouquets:
            show_bouquet_card(bot, call.message, choice(bouquets))
        else:
            bot.send_message(chat_id, "Каталог временно пуст.")
