from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.event_selection import user_data
from services.bouquet_service import get_all_bouquets
from keyboards.common import MAIN_MENU_CALLBACK, MAIN_MENU_TEXT, get_main_menu_inline_keyboard


import os

# Хранилище: какой букет сейчас смотрит пользователь
catalog_index = {}

def register_catalog_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "action:catalog")
    def show_catalog(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        
        if chat_id not in user_data:
            user_data[chat_id] = {}

        bouquets = get_all_bouquets()
        if not bouquets:
            bot.send_message(chat_id, "Каталог временно пуст.", reply_markup=get_main_menu_inline_keyboard())
            return

        # Сохраняем список всех букетов и начинаем с первого
        catalog_index[chat_id] = {
            'bouquets': bouquets,
            'index': 0
        }
        
        show_bouquet_with_nav(bot, call.message, chat_id, 0)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("nav:"))
    def handle_nav(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        action = call.data.split(":")[1]
        
        # Проверка, есть ли данные о каталоге
        if chat_id not in catalog_index:
            return
        
        state = catalog_index[chat_id]
        bouquets = state['bouquets']
        index = state['index']
        
        # Навигация вперёд/назад
        if action == "prev" and index > 0:
            index -= 1
        elif action == "next" and index < len(bouquets) - 1:
            index += 1
        else:
            return  # Достигли начала или конца
        
        # Обновляем индекс и показываем новый букет
        state['index'] = index
        bot.delete_message(chat_id, call.message.message_id)
        show_bouquet_with_nav(bot, call.message, chat_id, index)

def show_bouquet_with_nav(bot: TeleBot, message, chat_id: int, index: int):
    """Показывает букет с навигацией"""
    state = catalog_index[chat_id]
    bouquets = state['bouquets']
    bouquet = bouquets[index]
    
    # Сохраняем ID для заказа
    user_data[chat_id]["current_bouquet_id"] = bouquet.get("id")
    
    caption = (
        f"{bouquet['meaning']}\n\n"
        f"Состав: {bouquet['composition']}\n"
        f"Цена: {bouquet['price']} ₽\n\n"
        f"<b>Букет {index + 1} из {len(bouquets)}</b>\n\n"
        f"<b>Хотите что-то еще более уникальное?</b>\n"
        f"Подберите другой букет из нашей коллекции или закажите консультацию флориста"
    )
    
    # Создаём клавиатуру
    combined_kb = InlineKeyboardMarkup(row_width=2)
    combined_kb.add(InlineKeyboardButton("Заказать букет", callback_data="action:order"))
    combined_kb.add(
        InlineKeyboardButton("Консультация", callback_data="action:consult"),
        InlineKeyboardButton("Коллекция", callback_data="action:catalog")
    )
    combined_kb.add(
        InlineKeyboardButton("Назад", callback_data="nav:prev"),
        InlineKeyboardButton("Вперед", callback_data="nav:next")
    )
    combined_kb.add(InlineKeyboardButton(MAIN_MENU_TEXT, callback_data=MAIN_MENU_CALLBACK))
    
    try:
        # Импортируем модель для доступа к файлу
        from bot_app.models import Bouquet
        bouquet_obj = Bouquet.objects.get(id=bouquet["id"])
        
        if bouquet_obj.photo and os.path.exists(bouquet_obj.photo.path):

            with open(bouquet_obj.photo.path, 'rb') as photo_file:
                bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=combined_kb
                )
        else:
            # Если фото нет — отправляем только текст
            bot.send_message(chat_id, caption, reply_markup=combined_kb)
            print(f"[WARN] Фото не найдено для букета ID={bouquet['id']}")
            
    except Exception as e:
        bot.send_message(chat_id, f"{caption}\n\nФото временно недоступно", reply_markup=combined_kb)
        print(f"[ERROR] Ошибка отправки фото: {e}")
