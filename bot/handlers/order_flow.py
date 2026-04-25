# handlers/order_flow.py
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handlers.event_selection import user_data
from handlers.start import start_cmd, is_main_menu_text
from keyboards.common import get_main_menu_reply_keyboard
from keyboards.promo import get_promo_keyboard
from services.order_service import create_order_from_bot_payload
from services.notification_service import notify_courier_about_order
from services.promo_service import apply_promo_code
from services.django_bootstrap import ensure_django
from services.validators import validate_address, validate_delivery_datetime

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
            
        msg = bot.send_message(chat_id, "Введите ваше имя:", reply_markup=get_main_menu_reply_keyboard())
        bot.register_next_step_handler(msg, collect_name)

    def collect_name(message: Message):
        if is_main_menu_text(message.text):
            user_data.pop(message.chat.id, None)
            _processing_chats.discard(message.chat.id)
            start_cmd(bot, message)
            return
        if message.chat.id not in user_data: user_data[message.chat.id] = {}
        user_data[message.chat.id]["client_name"] = message.text.strip()
        msg = bot.send_message(
            message.chat.id,
            "Укажите адрес доставки:",
            reply_markup=get_main_menu_reply_keyboard(),
        )
        bot.register_next_step_handler(msg, collect_address)

    def collect_address(message: Message):
        if is_main_menu_text(message.text):
            user_data.pop(message.chat.id, None)
            _processing_chats.discard(message.chat.id)
            start_cmd(bot, message)
            return
        is_valid, address_or_error = validate_address(message.text)
        if not is_valid:
            msg = bot.send_message(
                message.chat.id,
                address_or_error,
                reply_markup=get_main_menu_reply_keyboard(),
            )
            bot.register_next_step_handler(msg, collect_address)
            return
        if message.chat.id not in user_data: user_data[message.chat.id] = {}
        user_data[message.chat.id]["address"] = address_or_error
        msg = bot.send_message(
            message.chat.id,
            "Укажите дату и время доставки (например: 15.05 в 14:00):",
            reply_markup=get_main_menu_reply_keyboard(),
        )
        bot.register_next_step_handler(msg, collect_datetime)

    def collect_datetime(message: Message):
        chat_id = message.chat.id

        if is_main_menu_text(message.text):
            user_data.pop(chat_id, None)
            _processing_chats.discard(chat_id)
            start_cmd(bot, message)
            return

        # Защита от повторного срабатывания
        if chat_id in _processing_chats:
            return

        is_valid, datetime_or_error = validate_delivery_datetime(message.text)
        if not is_valid:
            msg = bot.send_message(
                chat_id,
                datetime_or_error,
                reply_markup=get_main_menu_reply_keyboard(),
            )
            bot.register_next_step_handler(msg, collect_datetime)
            return

        _processing_chats.add(chat_id)

        if chat_id not in user_data: user_data[chat_id] = {}
        user_data[chat_id]["datetime"] = datetime_or_error
        
        ensure_django()
        from bot_app.models import Bouquet
        
        bouquet_id = user_data[chat_id].get('current_bouquet_id')
        bouquet = Bouquet.objects.filter(id=bouquet_id).first()
        if bouquet:
            amount = bouquet.price
        else:
            amount = 0
        user_data[chat_id]['amount'] = amount
        
        bot.send_message(
            chat_id,
            f'Сумма заказа: {amount} руб.\n\nУ вас есть промокод на скидку?',
            reply_markup=get_promo_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data == 'promo:yes')
    def handle_promo_yes(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        
        bot.edit_message_text(
            'Введите промокод:',
            chat_id=chat_id,
            message_id=call.message.message_id
        )

        bot.register_next_step_handler(call.message, apply_promo)
        
    def apply_promo(message: Message):
        chat_id = message.chat.id
        
        
        if is_main_menu_text(message.text):
            user_data.pop(chat_id, None)
            _processing_chats.discard(chat_id)
            start_cmd(bot, message)
            return
        
        promo_code = message.text
        amount = user_data[chat_id].get('amount', 0)
        
        result = apply_promo_code(promo_code, amount)
        
        if result['success']:
            user_data[chat_id]['promo_code'] = promo_code
            user_data[chat_id]['discount'] = result['discount']
            user_data[chat_id]['final_amount'] = result['final_amount']
            bot.send_message(
                chat_id,
                f'{result['message']}\n\n'
                f'Сумма заказа: {amount} руб.\n'
                f'Скидка: {result['discount']} руб.\n'
                f'Итого: {result['final_amount']} руб.'
            )
        else:
            bot.send_message(chat_id, result['message'])
            user_data[chat_id]['final_amount'] = amount
            user_data[chat_id]['discount'] = 0
            
        finalize_order(message)
        
    @bot.callback_query_handler(func=lambda call: call.data == 'promo:no')
    def handle_promo_no(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        
        bot.edit_message_text(
            'Продолжаем без промокода.',
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        
        user_data[chat_id]['final_amount'] = user_data[chat_id].get('amount', 0)
        user_data[chat_id]['discount'] = 0
        user_data[chat_id]['promo_code'] = None
        
        finalize_order(call.message)
        
    def finalize_order(message: Message):
        chat_id = message.chat.id

        payload = {
            "telegram_id": chat_id,
            "username": message.from_user.username if message.from_user else "",
            "bouquet_id": user_data[chat_id].get("current_bouquet_id"),
            "client_name": user_data[chat_id].get("client_name"),
            "address": user_data[chat_id].get("address"),
            "datetime": user_data[chat_id].get("datetime"),
            "phone": user_data[chat_id].get("phone"),
            "promo_code": user_data[chat_id].get("promo_code"),
            "discount": user_data[chat_id].get("discount", 0),
            "final_amount": user_data[chat_id].get(
                "final_amount",
                user_data[chat_id].get("amount", 0)
            )
        }
        
        order = create_order_from_bot_payload(payload)
        notify_courier_about_order(bot, order_data=order, payload=payload)
        
        discount = user_data[chat_id].get("discount", 0)
        final_amount = user_data[chat_id].get("final_amount", order['amount'])
        
        text = f"Заказ принят! Номер заказа: #{order['order_number']}.\n"
        if discount > 0:
            text += f'Итого к оплате: {final_amount} руб. (скидка {discount} руб.)\n\n'
        else:
            text += f'Итого к оплате: {final_amount} руб.\n\n'
        text += "Курьер свяжется с вами для уточнения деталей."
        
        bot.send_message(chat_id, text)
        
        # Очистка
        user_data.pop(chat_id, None)
        _processing_chats.discard(chat_id)
