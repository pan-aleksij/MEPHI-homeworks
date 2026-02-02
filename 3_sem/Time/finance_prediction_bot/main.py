import logging
from telegram.ext import Application
import config
from bot.handlers import setup_handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=config.BOT_LOG_FILE,
    encoding='utf-8'
)

def main():
    """
    Главная функция запуска бота
    """
    print("Запуск бота...")
    
    # Создаём приложение
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Настраиваем обработчики
    setup_handlers(application)
    
    print("Бот успешно запущен!")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()