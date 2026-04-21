"""
Временные данные. Ключи строго без пробелов!
"""
MOCK_BOUQUETS = [
    {
        "id": 1,
        "photo": "https://picsum.photos/seed/flower1/400/400.jpg",
        "meaning": "Этот букет несет в себе всю нежность ваших чувств и не способен оставить равнодушных ни одного сердца!",
        "composition": "Розы пионовидные ×3, Эвкалипт ×2, Лизиантус ×4",
        "price": 1200,
        "events": ["birthday", "wedding", "none"],
        "budget_tags": ["1000", "2000"]
    },
    {
        "id": 2,
        "photo": "https://picsum.photos/seed/flower2/400/400.jpg",
        "meaning": "Яркий и жизнерадостный букет для настоящих победителей!",
        "composition": "Подсолнухи ×5, Хризантемы ×3, Ромашки ×7",
        "price": 950,
        "events": ["birthday", "school", "none"],
        "budget_tags": ["500", "1000"]
    },
    {
        "id": 3,
        "photo": "https://picsum.photos/seed/flower3/400/400.jpg",
        "meaning": "Изысканная классика для особых случаев. Говорит о глубоком уважении и восхищении.",
        "composition": "Розы красные ×11, Гипсофила ×2",
        "price": 2500,
        "events": ["wedding", "birthday"],
        "budget_tags": ["2000", "more"]
    }
]

def get_bouquet_by_filters(event: str, budget: str) -> dict | None:
    import random
    filtered = [b for b in MOCK_BOUQUETS if event in b.get("events", [])]
    if not filtered:
        filtered = MOCK_BOUQUETS.copy()
    if budget != "any":
        filtered = [b for b in filtered if budget in b.get("budget_tags", [])]
    return random.choice(filtered) if filtered else None

def get_all_bouquets() -> list:
    return MOCK_BOUQUETS