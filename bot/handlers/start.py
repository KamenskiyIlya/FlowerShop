import os
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from keyboards.events import get_events_keyboard
from keyboards.common import MAIN_MENU_CALLBACK, MAIN_MENU_TEXT
from config.settings import MEDIA_ROOT
from services.user_service import upsert_tg_user, build_telegram_display_name


def register_start_handler(bot: TeleBot):
    
    @bot.message_handler(commands=['start'])
    def start_with_warning(message: Message):
        chat_id = message.chat.id
        tg_user = message.from_user
        if tg_user:
            display_name = build_telegram_display_name(
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )
            upsert_tg_user(telegram_id=tg_user.id, username=display_name)
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

    @bot.callback_query_handler(func=lambda call: call.data == MAIN_MENU_CALLBACK)
    def callback_main_menu(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        from handlers.event_selection import user_data
        user_data.pop(call.message.chat.id, None)
        start_cmd(bot, call.message)
        
    
    def show_main_menu(bot: TeleBot, message: Message):
        text = (
            "🌹 Добро пожаловать в FlowerShop!\n"
            "Закажите доставку праздничного букета, собранного специально для ваших близких.\n\n"
            "К какому событию готовимся? Выберите вариант или укажите свой:"
        )
        try:
            bot.send_message(message.chat.id, text, reply_markup=get_events_keyboard())
        except Exception as e:
            print(f"[START ERROR] {e}")


def start_cmd(bot, message):
    """Публичная функция для возврата в главное меню"""
    from keyboards.events import get_events_keyboard
    text = (
        "Добро пожаловать в FlowerShop!\n"
        "К какому событию готовимся?"
    )
    try:
        bot.send_message(message.chat.id, text, reply_markup=get_events_keyboard())
    except Exception as e:
        print(f"[START_CMD ERROR] {e}")           


def is_main_menu_text(text: str | None) -> bool:
    return (text or "").strip().lower() == MAIN_MENU_TEXT.lower()

