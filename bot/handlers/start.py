import os
from telebot import TeleBot
from telebot.types import Message
from keyboards.events import get_events_keyboard
from config.settings import MEDIA_ROOT


def register_start_handler(bot: TeleBot):
    
    @bot.message_handler(commands=['start'])
    def start_with_warning(message: Message):
        chat_id = message.chat.id
        warning_path = os.path.join(MEDIA_ROOT, 'pd_agreement.pdf')
        text = (
            '**Согласие на обработку персональных данных**\n\n'
            'Продолжая общение с ботом, вы даёте согласие на обработку '
            'персональных данных в соответствии с Федеральным законом '
            '№ 152-ФЗ «О персональных данных».\n\n'
            'Документ с условиями обработки приложен выше.\n\n'
            '✅ *Если вы согласны, просто продолжайте работу с ботом.*'
        )
        text_without_doc = (
            '**Согласие на обработку персональных данных**\n\n'
            'Продолжая общение с ботом, вы даёте согласие на обработку '
            'персональных данных в соответствии с Федеральным законом '
            '№ 152-ФЗ «О персональных данных».\n\n'
            '✅ *Если вы согласны, просто продолжайте работу с ботом.*'
        )
        
        try:
            if os.path.exists(warning_path):
                with open(warning_path, 'rb') as file:
                    bot.send_document(
                        chat_id,
                        file,
                        caption=text,
                        parse_mode='Markdown'
                    )

            else:
                bot.send_message(
                    chat_id,
                    text_without_doc,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f'[START ERROR] Не удалось отправить согласие: {e}')
            bot.send_message(
                chat_id,
                text_without_doc,
                parse_mode='Markdown'
            )
            
        show_main_menu(bot, message)
        
    
    def show_main_menu(bot: TeleBot, message: Message):
        text = (
            "🌹 Добро пожаловать в FlowerShop!\n"
            "Закажите доставку праздничного букета, собранного специально для ваших близких.\n\n"
            "К какому событию готовимся? Выберите вариант или укажите свой:"
        )
        
        bot.send_message(message.chat.id, text, reply_markup=get_events_keyboard())