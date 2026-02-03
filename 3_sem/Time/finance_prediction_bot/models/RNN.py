import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import root_mean_squared_error
from config import Config

class RNNModel():

    def __init__(self):
        self.n_steps = Config.RNN_N_STEPS  # количество временных шагов
        self.scaler = MinMaxScaler()
        self.last_data = None
        self.model = None
        self.data = None

    def create_sequences(self, data: np.ndarray, n_steps: int):
        """Создание последовательностей для RNN"""
        X, y = [], []
        for i in range(len(data) - n_steps):
            X.append(data[i:i + n_steps])
            y.append(data[i + n_steps])
        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        """Построение архитектуры RNN"""
        model = Sequential([
            SimpleRNN(50, activation='relu', return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            SimpleRNN(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model

    def train(self, data: pd.DataFrame, train_size: float = 0.8) -> float:
        # Извлекаем значения Close и нормализуем
        close_data = data['Close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(close_data)
        
        # Создаем последовательности
        X, y = self.create_sequences(scaled_data, self.n_steps)
        
        # Сохраняем последние данные для предсказания
        self.last_data = scaled_data[-self.n_steps:]
        
        # Разделение на train/test
        split_idx = int(len(X) * train_size)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Построение и обучение модели
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        self.model.fit(X_train, y_train, 
                      epochs=Config.RNN_EPOCHS,
                      batch_size=Config.RNN_BATCH_SIZE,
                      verbose=0,
                      validation_split=0.1)
        
        # Оценка на тестовой выборке
        predictions_scaled = self.model.predict(X_test, verbose=0)
        predictions = self.scaler.inverse_transform(predictions_scaled)
        y_test_actual = self.scaler.inverse_transform(y_test)
        
        rmse = root_mean_squared_error(y_test_actual, predictions)
        
        return rmse

    def predict(self, prediction_period: int) -> np.ndarray:
        predictions = []
        # Берем последнюю известную последовательность
        current_sequence = self.last_data.copy()
        
        for _ in range(prediction_period):
            # Предсказываем следующее значение
            current_sequence_reshaped = current_sequence.reshape(1, self.n_steps, 1)
            pred_scaled = self.model.predict(current_sequence_reshaped, verbose=0)[0]
            
            # Денормализуем предсказание
            pred = self.scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0, 0]
            predictions.append(pred)
            
            # Обновляем последовательность: удаляем первый элемент, добавляем новое предсказание
            current_sequence = np.append(current_sequence[1:], pred_scaled.reshape(1, 1), axis=0)
            
        return np.array(predictions)
