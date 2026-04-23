import re
from datetime import datetime

from services.django_bootstrap import ensure_django
from services.user_service import upsert_tg_user


def _parse_delivery_datetime(raw_value: str):
    value = (raw_value or "").strip()
    now = datetime.now()

    match = re.search(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?", value)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year_group = match.group(3)
        if year_group:
            year = int(year_group)
            if year < 100:
                year += 2000
        else:
            year = now.year
        try:
            delivery_date = datetime(year, month, day).date()
        except ValueError:
            delivery_date = now.date()
    else:
        delivery_date = now.date()

    time_match = re.search(r"(\d{1,2}:\d{2})", value)
    delivery_time = time_match.group(1) if time_match else value or "не указано"

    return delivery_date, delivery_time


def _build_order_number(Order):
    base = int(datetime.now().strftime("%y%m%d%H%M%S"))
    order_number = base
    while Order.objects.filter(order_number=order_number).exists():
        order_number += 1
    return order_number


def create_order_from_bot_payload(payload: dict) -> dict:
    ensure_django()

    from bot_app.models import Bouquet, Order

    telegram_id = payload.get("telegram_id")
    username = payload.get("username") or ""
    phone = payload.get("phone")
    bouquet_id = payload.get("bouquet_id")
    client_name = (payload.get("client_name") or "").strip()
    address = (payload.get("address") or "").strip()
    raw_datetime = payload.get("datetime") or ""
    final_amount = payload.get("final_amount", 0)
    discount = payload.get("discount", 0)
    promo_code = payload.get("promo_code")

    user = upsert_tg_user(
        telegram_id=telegram_id,
        username=username,
        phone=phone,
        fallback_name=client_name,
    )

    bouquet = Bouquet.objects.filter(id=bouquet_id).first()
    delivery_date, delivery_time = _parse_delivery_datetime(raw_datetime)
    order_number = _build_order_number(Order)
    
    if final_amount > 0:
        amount = final_amount
    else:
        if bouquet:
            amount = bouquet.price
        else:
            amount = 0


    order = Order.objects.create(
        order_number=order_number,
        user=user,
        bouquet=bouquet,
        address=address or "не указан",
        delivery_date=delivery_date,
        delivery_time=delivery_time,
        status="new",
        amount=amount,
    )

    return {
        "id": order.id,
        "order_number": order.order_number,
        "amount": order.amount,
        "delivery_date": str(order.delivery_date),
        "delivery_time": order.delivery_time,
    }
