#!/bin/bash

# Проверяем, что скрипт запущен из корневого каталога проекта
if [[ ! $(basename "$PWD") == "urfu_hackathon" ]]; then
    echo "Скрипт должен быть запущен из корневого каталога проекта."
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Загрузка данных
dvc pull --force

# Установка spaCy
python -m spacy download ru_core_news_sm

# Запуск парсера
echo "Запуск парсера..."
python src/html_parser.py

# Создание индекса
echo "Создание индекса..."
python src/build_index.py

# Запуск бота
echo "Запуск бота..."
python src/bot.py

# Деактивация виртуального окружения
deactivate
