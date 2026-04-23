from bot_app.models import Employee

def _safe_send(bot, chat_id: int, text: str) -> bool:
    if not chat_id:
        return False
    try:
        bot.send_message(chat_id, text)
        return True
    except Exception as exc:
        print(f"[NOTIFY ERROR] chat_id={chat_id}: {exc}")
        return False


def notify_director(bot, text: str):
    director = Employee.objects.filter(
        position='director',
        condition='work',
    ).firts()
    
    if not director:
        print("[NOTIFY] Внимание! Не найден активный директор для уведомления")
        return
    
    _safe_send(bot, director.telegram_id, text)


def notify_courier_about_order(bot, order_data: dict, payload: dict):
    couriers = Employee.objects.filter(
        position='courier',
        condition='work',
    )

    bouquet_id = payload.get("bouquet_id")
    client_name = payload.get("client_name") or "не указано"
    address = payload.get("address") or "не указан"
    delivery_dt = payload.get("datetime") or "не указано"
    customer_phone = payload.get("phone") or "не указан"
    telegram_id = payload.get("telegram_id") or "не указан"

    text = (
        "Новый заказ.\n"
        f"Номер: #{order_data['order_number']}\n"
        f"Клиент: {client_name}\n"
        f"Телефон: {customer_phone}\n"
        f"Telegram ID: {telegram_id}\n"
        f"Букет ID: {bouquet_id}\n"
        f"Сумма: {order_data['amount']} RUB\n"
        f"Адрес: {address}\n"
        f"Дата/время: {delivery_dt}"
    )
    
    if not couriers.exists():
        print('[NOTIFY] Внимание! Нет активных курьеров для уведомления о заказе.')
        notify_director(
            bot,
            f"Внимание! Нет активных курьеров для доставки заказа #{order_data['order_number']}."
            f'\n\n{text}',
        )
        return 
    
    for courier in couriers:
        _safe_send(bot, courier.telegram_id, text)


def notify_florist_about_consultation(bot, consultation_data: dict):
    florists = Employee.objects.filter(
        position='florist',
        condition='work',
    )
    
    text = (
        "Новая заявка на консультацию.\n"
        f"Заявка ID: {consultation_data.get('consultation_id') or 'не указан'}\n"
        f"Клиент: {consultation_data.get('client_name') or 'не указано'}\n"
        f"Телефон: {consultation_data.get('phone') or 'не указан'}\n"
        f"Telegram ID: {consultation_data.get('telegram_id') or 'не указан'}\n"
        f"Повод: {consultation_data.get('event') or 'не указан'}\n"
        f"Бюджет: {consultation_data.get('budget') or 'не указан'}\n"
        f"Текущий букет ID: {consultation_data.get('bouquet_id') or 'не указан'}"
    )
    
    if not florists.exists():
        print('[NOTIFY] Внимание! Нет активных флористов для уведомления о консультации.')
        notify_director(
            bot,
            'Внимание! Нет активных флористов для уведомления о консультации.',
        )
        return
    
    for florist in florists:
        _safe_send(bot, florist.telegram_id, text)
