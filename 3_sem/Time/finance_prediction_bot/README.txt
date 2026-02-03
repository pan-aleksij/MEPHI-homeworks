Структура проекта:
finance_prediction_bot
├── main.py
├── config.py
├── requirements.txt
├── README.txt
├── models
│ ├── ETS.py
│ ├── Random_Forest.py
│ └── RNN.py
├── services
│ ├── data_download.py
│ ├── forecast.py
│ └── train_models.py
├── logs
│ ├── logger.py
│ └── bot.log
└── bot
      └── bot_logics.py

Установка и запуск бота:
1. Клонируем репозиторий 
git clone https://github.com/pan-aleksij/MEPHI-homeworks/tree/main/3_sem/Time/finance_prediction_bot
cd finance_predictor_bot

2. Устанавливаем зависимости
pip install -r requirements.txt

3. В файле config.py устанавливаем свой токен
BOT_TOKEN: str = 'токен'

#токен можно получить у Tg бота @BotFather

4. Переходим в коревую директорию и запускаем файл main.py
cd finance_predictor_bot
python main.py

# при локальном запуске бывают проблемы с доступом к Yahoo finance если включен VPN