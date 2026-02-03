"""
Запуск бота
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from config import config
from bot.bot_logics import BotDial, TICKER, AMOUNT, PREDICTION_PERIOD
from logs.logger import setup_logging

# Настройка логирования 
setup_logging()
logger = logging.getLogger(__name__)


def build_conversation_handler() -> ConversationHandler:
    """Создаёт ConversationHandler"""
    return ConversationHandler(
        entry_points=[CommandHandler("start", BotDial.start)],
        states={
            TICKER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotDial.ticker_validation)
            ],
            AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotDial.amount_validation)
            ],
            PREDICTION_PERIOD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotDial.prediction_validation)
            ]
        },
        fallbacks=[CommandHandler("cancel", BotDial.cancel)],
    )

def main():
    """Главная функция запуска бота"""

    logger.info("=" * 60)
    logger.info("Telegram-бот запускается")
    logger.info("=" * 60)

    # Проверка токена
    if config.BOT_TOKEN == "":
        logger.error("Запросите токен у @BotFather и добавьте его в файл 'config.py'")
        return

    # Создание приложения
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Обработчик диалога
    conv_handler = build_conversation_handler()
    application.add_handler(conv_handler)

    # Добавление дополнительных обработчиков команд
    #application.add_handler(CommandHandler("help", BotDial.help_command))
    #application.add_handler(CommandHandler("stats", BotDial.stats_command))
    #application.add_handler(CommandHandler("settings", BotDial.settings_command))
    
    # Обработчик неизвестных команд
    #application.add_handler(MessageHandler(filters.COMMAND, BotDial.unknown_command))
    

    logger.info("Бот успешно запущен и готов к работе!")
    logger.info(f"Прогноз на {config.PREDICTION_PERIOD} дней")
    logger.info(f"История данных: {config.PERIOD_MONTH} дней")
    logger.info("-" * 60)

    # Запуск бота
    application.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()