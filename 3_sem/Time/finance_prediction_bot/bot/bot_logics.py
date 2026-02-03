'''
Логика бота, диалоги
'''

"""
Обработчики Telegram бота
"""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import config
from services.train_models import train_all_models

from services.data_download import check_ticker
from services.data_download import download_stock_data

from services.forecast import TradeRecommendation


logger = logging.getLogger(__name__)

# Состояния диалога
TICKER, AMOUNT, PREDICTION_PERIOD = range(3)

class BotDial:
    """
    Класс с основной логикой работы бота
    """

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            'Привет! Этот бот поможет спрогнозировать цены акций с помощью моделей машинного обучения!\n'
            f'Бот обучает модели на данных за последние {config.PERIOD_MONTH} месяца.\n'
            'Бот работает со следующими моделями:\n'
            '- ETS\n'
            '- Random Forest\n'
            '- RNN\n'
            '\n\nДля того чтобы начать выберете тикер. Например, NVDA или V.\n'
            'Затем выберите сумму и горизонт предсказания в днях (не больше месяца).',
            parse_mode='HTML'
        )
        return TICKER

    @staticmethod
    async def ticker_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ticker = update.message.text.strip().upper()  # Исправлено: сразу upper()
        
        if not check_ticker(ticker):
            await update.message.reply_text(f"Некорректный тикер {ticker}. Введите еще раз:", parse_mode='HTML')
            return TICKER
        
        context.user_data['ticker'] = ticker

        await update.message.reply_text("Укажите сумму инвестиций", parse_mode='HTML')
        return AMOUNT

    @staticmethod
    async def amount_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            amount = float(update.message.text.strip().replace(',', ''))

            if amount <= 0:
                await update.message.reply_text(
                    "Сумма должна быть положительной. Попробуйте еще раз:",
                    parse_mode='HTML'
                )
                return AMOUNT

            if amount > 1_000_000_000_000:
                await update.message.reply_text(
                    "Сумма слишком большая. Попробуйте еще раз:",
                    parse_mode='HTML'
                )
                return AMOUNT
            amount = float(update.message.text.strip().replace(',', ''))
            context.user_data["amount"] = amount

            await update.message.reply_text(
                "Укажите срок инвестиций (не больше месяца):",
                parse_mode='HTML'
            )
            return PREDICTION_PERIOD

        except ValueError:
            await update.message.reply_text(
                "❌ Некорректное число. Пожалуйста, введите число (например, 10000):"
            )
            return AMOUNT

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ <b>Произошла ошибка</b>\n\n"
                f"Детали: {str(e)}\n\n"
                "Попробуйте:\n"
                "• Проверить правильность тикера\n"
                "• Попробовать другую компанию\n"
                "• Повторить попытку через минуту\n\n"
                "Используйте /start для новой попытки.",
                parse_mode='HTML'
            )
            return ConversationHandler.END

    @staticmethod
    async def prediction_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            prediction_period = int(update.message.text.strip())  

            if prediction_period < 1:
                await update.message.reply_text(
                    "Срок должен быть не меньше одного дня. Попробуйте еще раз:",
                    parse_mode='HTML'
                )
                return PREDICTION_PERIOD

            if prediction_period > 31:
                await update.message.reply_text(
                    "Не больше месяца (31 день). Попробуйте еще раз:",
                    parse_mode='HTML'
                )
                return PREDICTION_PERIOD

            context.user_data["prediction_period"] = prediction_period

            await update.message.reply_text("Принято. Начинаю расчёт...", parse_mode='HTML')

            # Загрузка данных
            ticker = context.user_data.get('ticker')
            prediction_period = context.user_data.get('prediction_period')
            amount = context.user_data.get('amount')  

            data = download_stock_data(ticker)

            if data is None:
                await update.message.reply_text(
                    f"Не удалось загрузить данные для тикера <b>{ticker}</b>.\n"
                    "Возможные причины:\n"
                    "- Неверный тикер\n"
                    "- Проблемы с подключением к Yahoo Finance\n"
                    "- Тикер не торгуется на бирже\n\n"
                    "Используйте /start для новой попытки.",
                    parse_mode='HTML'
                )
                return ConversationHandler.END
            
            # обучение моделей
            trainer = train_all_models(data=data, prediction_period=prediction_period)
            forecast_df, historical_data, best_model_name, best_rmse = trainer.run(prediction_period)

            # Отправка результатов пользователю
            advisor = TradeRecommendation()
            result = advisor.Advise(forecast_df, historical_data)
            
            if result is not None:
                max_index, profit = result
                await update.message.reply_text(
                    f"Акцию: <b>{ticker}</b> можно покупать.\n"
                    f"Продать следует через <b>{max_index}</b> дней.\n"
                    f"Ожидаемый доход: <b>{(profit*100):.2f}%</b>\n"
                    f"Вложив <b>{amount}</b>, вы получите: <b>{amount*profit:.2f}</b>\n"
                    f"Лучшая модель:{best_model_name}, RMSE: {best_rmse:.2f}.",
                    parse_mode='HTML'
                )

                # Генерируем график и отправляем его
                filename = advisor.Plot_graph(forecast_df, historical_data)
                            
                # Отправляем фото
                with open(filename, 'rb') as photo:
                    await update.message.reply_photo(photo=photo)

                # Удаление временного файла
                os.remove(filename)

            else:
                await update.message.reply_text(
                    "Данную акцию не стоит покупать\n"
                    "Чтобы начать сначала нажмите /start", 
                    parse_mode='HTML'
                )

            return ConversationHandler.END

        except ValueError as ve:
            logger.error(f"ValueError в prediction_validation: {ve}", exc_info=True)
            await update.message.reply_text(
                "❌ Некорректное число. Введите срок в днях (например, 30):",
                parse_mode='HTML'
                )
            return PREDICTION_PERIOD

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ <b>Произошла ошибка</b>\n\n"
                f"Детали: {str(e)}\n\n"
                "Используйте /start для новой попытки.",
                parse_mode='HTML'
            )
            return ConversationHandler.END
        

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Отмена.\n\n"
            "Используйте /start для начала нового анализа."
        )
        return ConversationHandler.END
