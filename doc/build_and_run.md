# Как собрать и запустить проект

## Шаг 1: Установка Python 3.9 и создание работчей директории

Если у вас отсутствует Python 3.9, его можно установить через Miniconda

```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

Создаем окружение с Python 3.9 и активируем

```bash
conda create -y --name py39 python=3.9
conda activate py39
```

Создайте папку проекта

```bash
mkdir ~/pekgpt
cd ~/pekgpt
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
pip install dvc dvc-gdrive
dvc pull
```

При переходе по ссылке для выдачи пермишинов и редиректа на локалхост, при недоступности машины в локальной сети, можно скопировать url и в отдельном терминале запустить

```bash
wget url
```

## Шаг 3: Настройка окружения

Создайте файл `.env` в директории urfu_hackathon/src проекта 

```bash
nano src/.env
```

Добавьте в него следующие переменные:

```textplain
LL_MODEL=your_large_language_model_identifier
TOKEN=your_telegram_bot_token
```

Указываемая модель используется для создания эмбедингов, рекомендуется 'intfloat/multilingual-e5-large'

## Шаг 4: Установка и запуск webui

Перейдите в корень проекта (директорию pekgpt) и запустите установку Text generation web UI

```shell
./install_webui.sh
```

Запустите webui используя следующую команду:

```shell
./start_linux.sh --listen --model models/openchat_3.5.Q8_0.gguf --listen-port 7860
```

## Шаг 4: Установка зависимостей и запуск бота

Запустите чат-бота в отдельной консоли, используя следующую команду:

```shell
cd ~/pekgpt/urfu_hackathon/
./run_app.sh
```

Теперь бот готов к работе!