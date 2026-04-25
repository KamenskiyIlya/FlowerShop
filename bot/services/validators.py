import re
from datetime import datetime


def _normalize_spaces(value: str) -> str:
    return " ".join((value or "").strip().split())


def validate_phone(raw_value: str) -> tuple[bool, str]:
    digits = re.sub(r"\D", "", raw_value or "")

    if len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) != 11 or not digits.startswith("7"):
        return False, "Введите телефон в формате +7XXXXXXXXXX."

    return True, f"+{digits}"


def validate_address(raw_value: str) -> tuple[bool, str]:
    value = _normalize_spaces(raw_value)
    lower_value = value.lower()

    if len(value) < 8:
        return False, "Адрес слишком короткий. Укажите улицу и дом."

    if lower_value in {"-", ".", ",", "нет", "не знаю", "без адреса"}:
        return False, "Введите корректный адрес доставки (улица, дом, при необходимости квартира)."

    has_letters = any(ch.isalpha() for ch in value)
    has_digits = any(ch.isdigit() for ch in value)
    if not (has_letters and has_digits):
        return False, "Адрес должен содержать и название улицы, и номер дома."

    return True, value


def validate_delivery_datetime(raw_value: str) -> tuple[bool, str]:
    value = _normalize_spaces(raw_value)
    pattern = r"^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?\s*(?:в\s*)?(\d{1,2}):(\d{2})$"
    match = re.match(pattern, value, flags=re.IGNORECASE)

    if not match:
        return False, "Введите дату и время в формате: 15.05 в 14:00."

    day = int(match.group(1))
    month = int(match.group(2))
    year_group = match.group(3)
    hour = int(match.group(4))
    minute = int(match.group(5))

    if year_group:
        year = int(year_group)
        if year < 100:
            year += 2000
    else:
        year = datetime.now().year

    try:
        delivery_dt = datetime(year, month, day, hour, minute)
    except ValueError:
        return False, "Дата или время указаны некорректно. Пример: 15.05 в 14:00."

    if delivery_dt.date() < datetime.now().date():
        return False, "Дата доставки не может быть в прошлом."

    if hour < 8 or hour > 21:
        return False, "Время доставки должно быть в диапазоне 08:00-21:59."

    normalized = f"{delivery_dt.day:02d}.{delivery_dt.month:02d}.{delivery_dt.year:04d} в {delivery_dt.hour:02d}:{delivery_dt.minute:02d}"
    return True, normalized
