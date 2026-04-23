from services.django_bootstrap import ensure_django


def build_telegram_display_name(username: str | None, first_name: str | None, last_name: str | None) -> str:
    if (username or "").strip():
        return (username or "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part)
    return full_name.strip()


def upsert_tg_user(
    telegram_id: int,
    username: str | None = None,
    phone: str | None = None,
    fallback_name: str | None = None,
):
    ensure_django()

    from bot_app.models import TgUser

    if not telegram_id:
        raise ValueError("telegram_id is required")

    resolved_name = ((username or "").strip() or (fallback_name or "").strip() or f"user_{telegram_id}")
    normalized_phone = (phone or "").strip() or None

    user, _ = TgUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"username": resolved_name, "phone": normalized_phone},
    )

    updated_fields = []
    if resolved_name and user.username != resolved_name:
        user.username = resolved_name
        updated_fields.append("username")
    if normalized_phone and user.phone != normalized_phone:
        user.phone = normalized_phone
        updated_fields.append("phone")

    if updated_fields:
        user.save(update_fields=updated_fields)

    return user
