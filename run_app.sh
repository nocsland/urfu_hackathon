#!/bin/bash

# Проверяем, что скрипт запущен из корневого каталога проекта
if [[ ! $(basename "$PWD") == "urfu_hackathon" ]]; then
    echo "Скрипт должен быть запущен из корневого каталога проекта."
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Необходимо сначало инициализировать приложение, запустите init_app.sh"
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
echo "Запуск бота..."
python src/tg_bot.py

# Деактивация виртуального окружения
deactivate
