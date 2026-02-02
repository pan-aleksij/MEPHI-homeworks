import numpy as np

def calculate_rmse(actual, predicted):
    """
    Расчёт Root Mean Squared Error
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    mse = np.mean((actual - predicted) ** 2)
    rmse = np.sqrt(mse)
    
    return rmse

def calculate_mape(actual, predicted):
    """
    Расчёт Mean Absolute Percentage Error
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    # Избегаем деления на ноль
    mask = actual != 0
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    
    return mape

def calculate_mae(actual, predicted):
    """
    Расчёт Mean Absolute Error
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    mae = np.mean(np.abs(actual - predicted))
    
    return mae

def calculate_all_metrics(actual, predicted):
    """
    Расчёт всех метрик сразу
    """
    rmse = calculate_rmse(actual, predicted)
    mape = calculate_mape(actual, predicted)
    mae = calculate_mae(actual, predicted)
    
    metrics = {
        'RMSE': rmse,
        'MAPE': mape,
        'MAE': mae
    }
    
    return metrics

def print_metrics(metrics, model_name):
    """
    Красивый вывод метрик
    """
    print(f"\n=== Метрики модели {model_name} ===")
    print(f"RMSE: {metrics['RMSE']:.4f}")
    print(f"MAPE: {metrics['MAPE']:.2f}%")
    print(f"MAE: {metrics['MAE']:.4f}")
    print("=" * 40)