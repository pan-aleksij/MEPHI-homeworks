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
        ticker = user_data_storage[user_id]['ticker']
        
        await update.message.reply_text(
            f"Отлично! Начинаю анализ для {ticker} "
            f"с суммой ${amount:.2f}\n\n"
            f"Загружаю данные за последние 2 года..."
        )
        
        # НОВОЕ: Импорт и загрузка данных
        from services.data_service import download_stock_data, prepare_data
        
        # Загружаем данные
        raw_data = download_stock_data(ticker)
        
        if raw_data is None:
            await update.message.reply_text(
                f"❌ Не удалось загрузить данные для {ticker}.\n"
                f"Проверьте правильность тикера и попробуйте снова: /predict"
            )
            return ConversationHandler.END
        
        # Подготавливаем данные
        prepared_data = prepare_data(raw_data)
        
        await update.message.reply_text(
            f"✅ Данные загружены успешно!\n"
            f"Количество записей: {len(prepared_data)}\n"
            f"Период: {prepared_data['Date'].iloc[0].strftime('%Y-%m-%d')} — "
            f"{prepared_data['Date'].iloc[-1].strftime('%Y-%m-%d')}\n"
            f"Текущая цена: ${prepared_data['Close'].iloc[-1]:.2f}\n\n"
            f"Следующий этап: обучение моделей (будет в Части 3)"
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите число. Попробуйте ещё раз:"
        )
        return AMOUNT
    except Exception as e:
        await update.message.reply_text(
            f"Произошла ошибка: {str(e)}\n"
            f"Попробуйте снова: /predict"
        )
        return ConversationHandler.END

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