# Как собрать и запустить проект

## Шаг 1: Клонирование репозитория

Клонируйте репозиторий на свой локальный компьютер и перейдите в ветку webui:

```bash
git clone https://github.com/nocsland/urfu_hackathon.git
cd urfu_hackathon
git checkout webui
chmod 771 *.sh
```

Измените права на выполняемые скрипты

```bash
chmod 771 *.sh
```

Подгрузите файлы из хранилища

```bash
dvc pull
```

## Шаг 2: Настройка окружения

Создайте файл `.env` в директории urfu_hackathon/src проекта и добавьте в него следующие переменные:

```plaintext
TOKEN=your_telegram_bot_token
LL_MODEL=your_large_language_model_identifier
```

## Шаг 3: Установка webui

Запустите установку Text generation web UI

```shell
./urfu_hackathon/install_webui.sh
```

## Шаг 4: Установка зависимостей

Для начала работы с проектом вам понадобится Python версии ***3.9*** или выше. Инициализруйте приложение установив все необходимые зависимости и создав векторную базу, выполнив следующую команду:

```shell
./urfu_hackathon/init_app.sh
```

## Шаг 5: Запуск webui

Запустите webui, используя следующую команду:

```shell
./text-generation-webui/start_linux.sh --listen --model models/openchat_3.5.Q8_0.gguf --listen-port 7860
```

## Шаг 6: Запуск бота

Запустите чат-бота, используя следующую команду:

```shell
./urfu_hackathon/run_app.sh
```

Теперь бот готов к работе!