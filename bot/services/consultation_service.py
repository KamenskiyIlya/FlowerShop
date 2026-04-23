from services.django_bootstrap import ensure_django


def create_consultation_from_bot_payload(payload: dict) -> dict:
    ensure_django()

    from bot_app.models import Bouquet, Consultation, TgUser

    telegram_id = payload.get("telegram_id")
    username = payload.get("username") or ""
    phone = (payload.get("phone") or "").strip()
    event = payload.get("event")
    budget = payload.get("budget")
    bouquet_id = payload.get("bouquet_id")

    user, _ = TgUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"username": username or f"user_{telegram_id}", "phone": phone or None},
    )

    updated_fields = []
    if username and user.username != username:
        user.username = username
        updated_fields.append("username")
    if phone and user.phone != phone:
        user.phone = phone
        updated_fields.append("phone")
    if updated_fields:
        user.save(update_fields=updated_fields)

    bouquet = Bouquet.objects.filter(id=bouquet_id).first()

    consultation = Consultation.objects.create(
        user=user,
        phone=phone or "не указан",
        event=event or None,
        budget=budget or None,
        initial_bouquet=bouquet,
        status="new",
    )

    return {
        "id": consultation.id,
        "status": consultation.status,
        "phone": consultation.phone,
    }
