import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

def download_stock_data(ticker):
    """
    Загрузка данных по тикеру за последние 2 года
    """
    print(f"Загружаю данные для {ticker}...")
    
    # Вычисляем даты
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * config.DATA_PERIOD_YEARS)
    
    try:
        # Загружаем данные
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"Ошибка: данные для {ticker} не найдены")
            return None
        
        print(f"Загружено {len(df)} записей")
        return df
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return None

def prepare_data(df):
    """
    Подготовка данных для моделей
    """
    if df is None or df.empty:
        return None
    
    # Оставляем только цену закрытия
    data = pd.DataFrame()
    data['Date'] = df.index
    data['Close'] = df['Close'].values
    data = data.reset_index(drop=True)
    
    # Удаляем пропуски
    data = data.dropna()
    
    print(f"Данные подготовлены: {len(data)} записей")
    return data

def create_lagged_features(data, n_lags=5):
    """
    Создание лаговых признаков для ML моделей
    """
    df = data.copy()
    
    # Создаём лаги
    for i in range(1, n_lags + 1):
        df[f'lag_{i}'] = df['Close'].shift(i)
    
    # Добавляем скользящие средние
    df['ma_7'] = df['Close'].rolling(window=7).mean()
    df['ma_30'] = df['Close'].rolling(window=30).mean()
    
    # Удаляем строки с NaN
    df = df.dropna()
    
    return df

def split_data(data, test_size=None):
    """
    Разделение данных на обучающую и тестовую выборки
    """
    if test_size is None:
        test_size = config.TEST_SIZE
    
    # Вычисляем размер теста
    split_idx = int(len(data) * (1 - test_size))
    
    train_data = data[:split_idx]
    test_data = data[split_idx:]
    
    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")
    
    return train_data, test_data

def normalize_data(train_data, test_data, column='Close'):
    """
    Нормализация данных
    """
    # Находим min и max на обучающей выборке
    min_val = train_data[column].min()
    max_val = train_data[column].max()
    
    # Нормализуем
    train_normalized = train_data.copy()
    test_normalized = test_data.copy()
    
    train_normalized[column] = (train_data[column] - min_val) / (max_val - min_val)
    test_normalized[column] = (test_data[column] - min_val) / (max_val - min_val)
    
    # Возвращаем также параметры нормализации
    scaler_params = {'min': min_val, 'max': max_val}
    
    return train_normalized, test_normalized, scaler_params

def denormalize_data(data, scaler_params):
    """
    Обратная нормализация данных
    """
    min_val = scaler_params['min']
    max_val = scaler_params['max']
    
    return data * (max_val - min_val) + min_val