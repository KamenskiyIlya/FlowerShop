import random
from services.django_bootstrap import ensure_django


def _normalize_event(event: str | None) -> str | None:
    if not event:
        return None
    if event == "none":
        return "no_reason"
    return event


def _apply_budget_filter(queryset, budget: str | None):
    if not budget or budget == "any":
        return queryset
    if budget == "500":
        return queryset.filter(price__lte=750)
    if budget == "1000":
        return queryset.filter(price__gt=750, price__lte=1500)
    if budget == "2000":
        return queryset.filter(price__gt=1500, price__lte=3000)
    if budget == "more":
        return queryset.filter(price__gt=3000)
    return queryset


def _serialize_bouquet(bouquet) -> dict:
    photo_value = ""
    photo_name = str(bouquet.photo) if bouquet.photo else ""

    if photo_name.startswith(("http://", "https://")):
        photo_value = photo_name
    elif photo_name:
        try:
            photo_value = bouquet.photo.path
        except Exception:
            photo_value = photo_name

    return {
        "id": bouquet.id,
        "photo": photo_value,
        "meaning": bouquet.meaning,
        "composition": bouquet.composition,
        "price": bouquet.price,
    }


def get_bouquet_by_filters(event: str | None, budget: str | None) -> dict | None:
    ensure_django()
    from bot_app.models import Bouquet

    normalized_event = _normalize_event(event)
    queryset = Bouquet.objects.filter(in_stock=True)

    if normalized_event in {"birthday", "wedding", "school", "no_reason", "other"}:
        queryset = queryset.filter(occasion=normalized_event)

    queryset = _apply_budget_filter(queryset, budget)

    total = queryset.count()
    if total == 0:
        return None

    bouquet = queryset[random.randrange(total)]
    return _serialize_bouquet(bouquet)


def get_all_bouquets() -> list[dict]:
    ensure_django()
    from bot_app.models import Bouquet

    bouquets = Bouquet.objects.filter(in_stock=True).order_by("id")
    return [_serialize_bouquet(bouquet) for bouquet in bouquets]
