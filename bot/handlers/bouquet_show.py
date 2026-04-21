# handlers/bouquet_show.py
from telebot import TeleBot
from telebot.types import Message
from keyboards.actions import get_bouquet_actions_keyboard
from handlers.event_selection import user_data

def show_bouquet_card(bot: TeleBot, message: Message, bouquet: dict):
    chat_id = message.chat.id
    
    # Безопасная инициализация сессии (если её нет или она была очищена)
    if chat_id not in user_data:
        user_data[chat_id] = {}
        
    user_data[chat_id]["current_bouquet_id"] = bouquet.get("id")

    caption = (
        f"{bouquet['meaning']}\n\n"
        f"Состав: {bouquet['composition']}\n"
        f"Цена: {bouquet['price']} ₽\n\n"
        f"<b>Хотите что-то еще более уникальное?</b>\n"
        f"Подберите другой букет из нашей коллекции или закажите консультацию флориста"
    )

    try:
        bot.send_photo(
            chat_id=chat_id,
            photo=bouquet["photo"],
            caption=caption,
            parse_mode="HTML",  # HTML стабильнее Markdown
            reply_markup=get_bouquet_actions_keyboard()
        )
    except Exception as e:
        bot.send_message(chat_id, caption, reply_markup=get_bouquet_actions_keyboard())
        print(f"[WARN] Не удалось загрузить фото: {e}")