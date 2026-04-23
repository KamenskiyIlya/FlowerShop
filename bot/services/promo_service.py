from bot_app.models import PromoCode
from services.django_bootstrap import ensure_django


def apply_promo_code(code: str, amount: int) -> dict:
    ensure_django()
    
    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return {
            'success':  False,
            'message': '❌ Промокод не найден'
        }
        
    if not promo.is_valid:
        return {
            'success': False,
            'message': '❌ Промокод недействителен или истёк'
        }
    
    discount = promo.discount
    final_amount = amount - discount
    
    return {
        'success': True,
        'discount': discount,
        'final_amount': final_amount,
        'message': f'✅ Промокод применён! Скидка {discount} руб.'
    }