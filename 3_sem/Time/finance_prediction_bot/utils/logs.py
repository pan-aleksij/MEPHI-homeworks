import datetime
import os

def log_request(user_id, ticker, amount, model_name, metric_value, profit):
    """
    Логирование запроса пользователя в файл
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_line = f"{timestamp}|{user_id}|{ticker}|{amount}|{model_name}|{metric_value:.4f}|{profit:.2f}\n"
    
    # Создаём файл если его нет
    if not os.path.exists('logs.txt'):
        with open('logs.txt', 'w', encoding='utf-8') as f:
            f.write("Timestamp|UserID|Ticker|Amount|Model|Metric|Profit\n")
    
    # Добавляем запись
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    print(f"Logged request: User {user_id}, Ticker {ticker}")
    