# Как собрать и запустить проект

## Шаг 0: Установка Python 3.9

Если у вас отсутствует Python 3.9, его можно установить через Miniconda

```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
```

Создаем окружение с Python 3.9 и активируем

```bash
conda create --name py39 python=3.9
conda activate py39
```

## Шаг 1: Создайте папку проекта

```bash
mkdir pekgpt
cd pekgpt
```

## Шаг 2: Клонирование репозитория

Клонируйте репозиторий на свой локальный компьютер и перейдите в ветку webui:

```bash
git clone https://github.com/nocsland/urfu_hackathon.git
cd urfu_hackathon
git checkout webui
```

Измените права на выполняемые скрипты

```bash
chmod 771 *.sh
```

Подгрузите файлы из хранилища

```bash
dvc pull
```

## Шаг 3: Настройка окружения

Создайте файл `.env` в директории urfu_hackathon/src проекта и добавьте в него следующие переменные:

```shell
LL_MODEL=your_large_language_model_identifier > scr/.env
TOKEN=your_telegram_bot_token >> scr/.env
```

Указываемая модель используется для создания эмбедингов, рекомендуется 'intfloat/multilingual-e5-large'

## Шаг 4: Установка webui

Перейдите в корень проекта (директорию pekgpt) и запустите установку Text generation web UI

```shell
./urfu_hackathon/install_webui.sh
```

## Шаг 4: Установка зависимостей

Запустите чат-бота, используя следующую команду:

```shell
./urfu_hackathon/run_app.sh
```

## Шаг 5: Запуск webui

Запустите webui, используя следующую команду:

```shell
./text-generation-webui/start_linux.sh --listen --model models/openchat_3.5.Q8_0.gguf --listen-port 7860
```

Теперь бот готов к работе!