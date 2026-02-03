'''
загрузка и обработка данных
'''

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)



@staticmethod
def download_stock_data(ticker):
    """
    Загрузка данных по тикеру за последние 2 года
    """
    print(f"Загружаю данные для {ticker}...")
    ticker = str(ticker.upper())
    
    # Вычисляем даты
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 2)
    
    try:
        # Используйте yf.download вместо Ticker.history
        df = yf.download(
            ticker, 
            start=start_date, 
            end=end_date,
            progress=False,  # Отключаем progress bar
            auto_adjust=True  # Автоматическая корректировка цен
        )
        
        if df.empty:
            logger.error(f"Данные для {ticker} не найдены")
            return None
            
        # Возвращаем только цену закрытия
        df = df[['Close']]
        logger.info(f"Загружено {len(df)} записей для {ticker}")
        return df
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных для {ticker}: {e}")
        return None


    

@staticmethod
def check_ticker(ticker):
    ticker = str(ticker.upper())
    is_ticker = yf.Ticker(ticker)
    try:
        info = is_ticker.info
        # Проверяем, что словарь не пустой и содержит ключ 'symbol' 
        if info and 'symbol' in info:
            return True
        return False
    except Exception:
        # Ловим любые ошибки, включая 404 и проблемы с соединением
        return True

