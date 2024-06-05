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

# Проверяем наличие CUDA
if [ -d /usr/local/cuda ]; then
  echo "CUDA detected!"
  export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
  export FORCE_CMAKE=1
  pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
  pip install --upgrade --force-reinstall faiss-gpu --no-cache-dir
else
  echo "CUDA not detected!"
  pip install llama-cpp-python
  pip install faiss-cpu
fi

# Загрузка данных
dvc pull --force

# Установка spaCy
python -m spacy download ru_core_news_sm

# Парсер
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
