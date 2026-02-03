"""
Random Forest модель для прогнозирования
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from config import Config


class RandomForestModel:
    def __init__(self):
        self.name = "Random Forest"
        self.n_lags = Config.RF_N_LAGS
        self.last_data = None
        self.data = None

    def create_lag_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Создание лаговых признаков"""
        df = data.copy()

        # лаги (5 дней - рабочая неделя)
        df['Lag_5'] = df['Close'].shift(5)
        # две рабочие недели
        df['Lag_10'] = df['Close'].shift(10)
        # 30 дней
        df['Lag_30'] = df['Close'].shift(30)

        # скользящее среднее
        df['rolling_mean_5'] = df['Close'].rolling(window=5).mean()
        df['rolling_mean_10'] = df['Close'].rolling(window=10).mean()
        df['rolling_mean_30'] = df['Close'].rolling(window=30).mean()


        return df.dropna()

    def train(self, data: pd.DataFrame, train_size: float = 0.8) -> float:
        df_features = self.create_lag_features(data)
        
        # Сохраняем последние данные для последующего предсказания
        self.last_data = df_features.iloc[-1:]
        
        # Разделение на признаки (X) и целевую переменную (y)
        X = df_features.drop('Close', axis=1)
        y = df_features['Close']
        
        split_idx = int(len(X) * train_size)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        self.model.fit(X_train, y_train)
        
        predictions = self.model.predict(X_test)
        rmse = root_mean_squared_error(y_test, predictions)
        

        return rmse

    def predict(self, prediction_period) -> np.ndarray:
        predictions = []
        # Берем последнюю известную строку признаков
        current_features = self.last_data.drop('Close', axis=1).values
        
        for _ in range(prediction_period):
            # Предсказываем следующее значение
            pred = self.model.predict(current_features)[0]
            predictions.append(pred)
            
            current_features = current_features 
            
        return np.array(predictions)


