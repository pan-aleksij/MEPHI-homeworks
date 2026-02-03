"""
ETS модель для прогнозирования
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import root_mean_squared_error
from config import Config

class ETSModel:

    def __init__(self):
        self.model_name = "ETS"
        self.model = None
        self.last_data = None
        self.data = None
        # Параметры модели ETS
        self.trend = Config.ETS_TREND if hasattr(Config, 'ETS_TREND') else 'add'
        self.seasonal = Config.ETS_SEASONAL if hasattr(Config, 'ETS_SEASONAL') else 'add'
        self.seasonal_periods = Config.ETS_SEASONAL_PERIODS if hasattr(Config, 'ETS_SEASONAL_PERIODS') else 12

    def prepare_data(self, data: pd.DataFrame) -> pd.Series:
        """Подготовка данных для ETS модели"""
        df = data.copy()
        
        # Убедимся, что индекс - это дата
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
        
        # Сортируем по дате
        df = df.sort_index()
        
        return df['Close']

    def train(self, data: pd.DataFrame, train_size: float = 0.8) -> float:
        series = self.prepare_data(data)
        
        # Разделение на train и test
        split_idx = int(len(series) * train_size)
        train_series = series.iloc[:split_idx]
        test_series = series.iloc[split_idx:]
        
        # Сохраняем последние данные для последующего предсказания
        self.last_data = series
        
        # Обучаем модель на тренировочных данных
        try:
            self.model = ExponentialSmoothing(
                train_series,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods
            ).fit()
        except:
            # Если не удается с сезонностью, попробуем без нее
            self.model = ExponentialSmoothing(
                train_series,
                trend=self.trend,
                seasonal=None
            ).fit()
        
        # Предсказываем на тестовом периоде
        predictions = self.model.forecast(steps=len(test_series))
        rmse = root_mean_squared_error(test_series, predictions)
        
        # Переобучаем модель на всех данных для финального использования
        try:
            self.model = ExponentialSmoothing(
                series,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods
            ).fit()
        except:
            self.model = ExponentialSmoothing(
                series,
                trend=self.trend,
                seasonal=None
            ).fit()
        
        return rmse

    def predict(self, prediction_period: int) -> np.ndarray:
        """Прогнозирование на заданный период"""
        if self.model is None:
            raise ValueError("Модель не обучена. Сначала вызовите метод train()")
        
        # ETS модель может предсказывать на несколько шагов вперед сразу
        predictions = self.model.forecast(steps=prediction_period)
        
        return np.array(predictions)