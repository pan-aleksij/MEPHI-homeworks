from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Состояния диалога
TICKER, AMOUNT = range(2)

# Временное хранилище данных пользователя
user_data_storage = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    """
    await update.message.reply_text(
        "Привет! Я бот для прогнозирования акций.\n\n"
        "Отправь мне команду /predict чтобы начать анализ."
    )

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса прогнозирования
    """
    await update.message.reply_text(
        "Введите тикер компании (например: AAPL, MSFT, GOOGL):"
    )
    return TICKER

async def get_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение тикера от пользователя
    """
    user_id = update.effective_user.id
    ticker = update.message.text.upper().strip()
    
    # Сохраняем тикер
    if user_id not in user_data_storage:
        user_data_storage[user_id] = {}
    user_data_storage[user_id]['ticker'] = ticker
    
    await update.message.reply_text(
        f"Тикер: {ticker}\n"
        f"Теперь введите сумму для инвестиции (в долларах):"
    )
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение суммы инвестиции
    """
    user_id = update.effective_user.id
    
    try:
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text(
                "Сумма должна быть положительной. Попробуйте ещё раз:"
            )
            return AMOUNT
        
        user_data_storage[user_id]['amount'] = amount
        
        await update.message.reply_text(
            f"Отлично! Начинаю анализ для {user_data_storage[user_id]['ticker']} "
            f"с суммой ${amount:.2f}\n\n"
            f"Загружаю данные и обучаю модели... Это может занять несколько минут."
        )
        
        # Здесь будет вызов функции прогнозирования
        # Пока просто заглушка
        ticker = user_data_storage[user_id]['ticker']
        await update.message.reply_text(
            f"[Заглушка] Анализ для {ticker} выполнен!\n"
            f"В следующих частях добавим реальную функциональность."
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите число. Попробуйте ещё раз:"
        )
        return AMOUNT

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена операции
    """
    await update.message.reply_text(
        "Операция отменена. Используйте /predict чтобы начать заново."
    )
    return ConversationHandler.END

def setup_handlers(application: Application):
    """
    Настройка всех обработчиков бота
    """
    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('predict', predict_command)],
        states={
            TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ticker)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(conv_handler)