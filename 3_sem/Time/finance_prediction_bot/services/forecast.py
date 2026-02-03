'''
рекомендации и построение графика
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class TradeRecommendation:
    def Advise(self, forecast_df: pd.DataFrame, historical_data: pd.DataFrame):
        last_value= historical_data.iloc[-2, 0]
        actual_price = pd.to_numeric(last_value, errors="coerce")
        max_value_forecast = forecast_df.iloc[:, 0].max()
        max_index_forecast = forecast_df.iloc[:, 0].idxmax()

        if (actual_price > max_value_forecast):
            return None
        else:
            profit = max_value_forecast / actual_price
            return max_index_forecast, profit

    def Plot_graph(
        self,
        forecast_df: pd.DataFrame,
        historical_data: pd.DataFrame,
        filename: str = "forecast_plot.png",
    ):
        import pandas as pd
        import matplotlib.pyplot as plt

        start = pd.Timestamp.today().normalize()

        forecast_df = forecast_df.copy()
        forecast_df.index = pd.date_range(start=start, periods=len(forecast_df), freq="D")
        forecast_df.index.name = "date"  # опционально
                                  
        # --- Валидация входных данных ---
        if historical_data is None or historical_data.empty:
            raise ValueError("historical_data пустой или None")
        if forecast_df is None or forecast_df.empty:
            raise ValueError("forecast_df пустой или None")

        if historical_data.shape[1] != 1:
            raise ValueError(f"В historical_data должна быть ровно 1 колонка, сейчас: {historical_data.shape[1]}")
        if forecast_df.shape[1] != 1:
            raise ValueError(f"В forecast_df должна быть ровно 1 колонка, сейчас: {forecast_df.shape[1]}")

        hist_col = historical_data.columns[0]
        fc_col = forecast_df.columns[0]

        # На всякий случай приведём индекс к datetime, если он похож на даты
        for df in (historical_data, forecast_df):
            if not isinstance(df.index, pd.DatetimeIndex):
                try:
                    df.index = pd.to_datetime(df.index)
                except Exception:
                    pass

        # --- Рисуем ---
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 5), constrained_layout=True)

        # Слева: исторические данные (последний месяц)
        axes[0].plot(historical_data.index, historical_data[hist_col], linewidth=2)
        axes[0].set_title("История цены (последний месяц)")
        axes[0].set_xlabel("Дата")
        axes[0].set_ylabel("Цена")
        axes[0].grid(True, alpha=0.3)

        # Справа: прогноз на ближайшие дни
        axes[1].plot(forecast_df.index, forecast_df[fc_col], linewidth=2, color="tab:orange")
        axes[1].set_title(f"Прогноз (следующие {len(forecast_df)} дней)")
        axes[1].set_xlabel("Дата")
        axes[1].set_ylabel("Цена")
        axes[1].grid(True, alpha=0.3)

        # 
        fig.autofmt_xdate(rotation=30)

        # Сохраняем график в файл
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close(fig)

        return filename