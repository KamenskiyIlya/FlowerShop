from telebot import TeleBot
from telebot.types import Message
from keyboards.events import get_events_keyboard

def register_start_handler(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start_cmd(message: Message):
        text = (
            "Добро пожаловать в FlowerShop!\n"
            "Закажите доставку праздничного букета, собранного специально для ваших близких.\n\n"
            "К какому событию готовимся? Выберите вариант или укажите свой:"
        )
        try:
            bot.send_message(message.chat.id, text, reply_markup=get_events_keyboard())
        except Exception as e:
            print(f"[START ERROR] {e}")