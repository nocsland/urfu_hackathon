#!/bin/bash

# Проверяем, что скрипт запущен из корневого каталога проекта
if [[ ! $(basename "$PWD") == "urfu_hackathon" ]]; then
    echo "Скрипт должен быть запущен из корневого каталога проекта."
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Запуск бота
echo "Запуск бота..."
python src/start_app.py

# Деактивация виртуального окружения
deactivate
