"""
Конфигурация бота
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Конфигурация бота"""

    # Telegram
    BOT_TOKEN: str = '8417241095:AAH8Y6B7mW2vsWdNmBQPB9VzXp9Q9MRFSrc'

    # Параметры данных
    PERIOD_MONTH = int(12)
    PREDICTION_PERIOD = int(30)

    # Параметры обучения RNN
    RNN_N_STEPS = 60  # количество временных шагов (например, 60 дней)
    RNN_EPOCHS = 50
    RNN_BATCH_SIZE = 32

    # Random Forest
    RF_N_ESTIMATORS: int = 100
    RF_MAX_DEPTH: int = 10
    RF_N_LAGS: int = 30

    

    # Логирование
    LOG_FILE: str = 'logs.txt'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Визуализация
    FIGURE_SIZE: tuple = (12, 6)



config = Config()