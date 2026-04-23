from services.django_bootstrap import ensure_django
from services.user_service import upsert_tg_user


def create_consultation_from_bot_payload(payload: dict) -> dict:
    ensure_django()

    from bot_app.models import Bouquet, Consultation

    telegram_id = payload.get("telegram_id")
    username = payload.get("username") or ""
    phone = (payload.get("phone") or "").strip()
    event = payload.get("event")
    budget = payload.get("budget")
    bouquet_id = payload.get("bouquet_id")

    user = upsert_tg_user(
        telegram_id=telegram_id,
        username=username,
        phone=phone,
    )

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
