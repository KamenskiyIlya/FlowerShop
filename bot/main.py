import telebot
import traceback
from config.settings import settings
from handlers.start import register_start_handler
from handlers.event_selection import register_event_handler
from handlers.budget_selection import register_budget_handler
from handlers.order_flow import register_order_handler
from handlers.consultation_flow import register_consultation_handler
from handlers.catalog import register_catalog_handler

def main():
    if not settings.BOT_TOKEN:
        print("Ошибка: BOT_TOKEN не найден в .env")
        return

    bot = telebot.TeleBot(settings.BOT_TOKEN, parse_mode="HTML", threaded=False)

    register_start_handler(bot)
    register_event_handler(bot)
    register_budget_handler(bot)
    register_order_handler(bot)
    register_consultation_handler(bot)
    register_catalog_handler(bot)

    # Ловим неизвестные команды, чтобы бот не падал
    @bot.message_handler(func=lambda m: True)
    def fallback(message):
        bot.reply_to(message, "Используйте /start для начала работы 🌸")

    print("FlowerShop Bot запущен...")
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        print("Критическая ошибка:")
        traceback.print_exc()

if __name__ == "__main__":
    main()