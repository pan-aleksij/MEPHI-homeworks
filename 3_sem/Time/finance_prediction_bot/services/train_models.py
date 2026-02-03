import logging
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from models.ETS import ETSModel
from models.Random_Forest import RandomForestModel
from models.RNN import RNNModel

logger = logging.getLogger(__name__)

class train_all_models:
    """Класс для обучения всех моделей и выбора лучшей"""

    def __init__(self, data: pd.DataFrame, prediction_period: int):
        """
        Args:
            data: DataFrame со значением цены акции на конец каждого дня
            prediction_period: Количество дней для предсказания
        """
        self.data = data
        self.prediction_period = prediction_period
        
        # Инициализация моделей
        self.models = {
            'ETS': ETSModel(),
            'Random Forest': RandomForestModel(),
            'RNN': RNNModel()
        }
        
        self.best_model_name: Optional[str] = None
        self.best_rmse: float = float('inf')
        self.results: Dict[str, float] = {}
        self.forecast_df: Optional[pd.DataFrame] = None
        self.historical_data: Optional[pd.DataFrame] = None

    def find_best_model(self) -> Tuple[str, float]:
        """
        Обучает все модели и находит лучшую по метрике RMSE
        
        Returns:
            Tuple[str, float]: (название лучшей модели, ее RMSE)
        """
        results = {}

        for name, model in self.models.items():
            logger.info(f"Обучение модели {name}...")
            try:
                rmse = model.train(self.data)
                results[name] = rmse
                logger.info(f"{name}: RMSE = {rmse:.4f}")
            except Exception as e:
                logger.error(f"Ошибка обучения {name}: {e}")
                results[name] = float('inf')

        # Сохранение результатов
        self.results = results
        
        # Выбор лучшей модели (с минимальным RMSE)
        self.best_model_name = min(results.keys(), key=lambda k: results[k])
        self.best_rmse = results[self.best_model_name]

        logger.info(f"Лучшая модель: {self.best_model_name} (RMSE={self.best_rmse:.4f})")

        return self.best_model_name, self.best_rmse

    def make_prediction(self, prediction_period):
        """Создает прогноз на заданный период для лучшей модели"""
        if self.best_model_name is None:
            raise ValueError("Сначала необходимо найти лучшую модель. Вызовите метод find_best_model()")
        
        # Получаем лучшую модель
        best_model = self.models[self.best_model_name]
        
        # Делаем прогноз
        logger.info(f"Создание прогноза на {self.prediction_period} дней с помощью {self.best_model_name}...")
        predictions = best_model.predict(self.prediction_period)
        
        # Создаем DataFrame с прогнозом
        self.forecast_df = pd.DataFrame({
            'Forecast': predictions
        })
        
        # Получаем исторические данные за последний месяц (30 дней)
        self.historical_data = self.data.tail(30).copy()
        
        logger.info(f"Прогноз успешно создан")

    def run(self, prediction_period: int) -> Tuple[pd.DataFrame, pd.DataFrame, str, float]:
        """
        Запуск полного процесса: обучение, выбор лучшей модели и прогнозирование
        
        Returns:
            Tuple содержащий:
                - forecast_df: DataFrame с прогнозом (один столбец)
                - historical_data: DataFrame с историческими данными (месяц до прогноза)
                - best_model_name: Название лучшей модели
                - best_rmse: RMSE лучшей модели
        """
        # Находим лучшую модель
        self.find_best_model()
        
        # Делаем прогноз
        self.make_prediction(prediction_period)
        
        return (
            self.forecast_df,
            self.historical_data,
            self.best_model_name,
            self.best_rmse
        )

    def get_results_summary(self) -> Dict[str, any]:
        """Получить сводку результатов всех моделей"""
        return {
            'best_model': self.best_model_name,
            'best_rmse': self.best_rmse,
            'all_results': self.results
        }
    