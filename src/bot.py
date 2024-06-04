import os
import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
from main import get_answer

# Загрузка переменных окружения из .env файла
load_dotenv()
# Чтение API-токена из переменной среды
TOKEN = os.getenv('BOT_API_TOKEN')
INDEX_PASSWORD = os.getenv('INDEX_PASSWORD')  # Чтение пароля из переменной среды

executor = ThreadPoolExecutor()
awaiting_password = False  # Флаг для ожидания ввода пароля

# Функция для отправки клавиатуры "Загрузка файла" и "Переиндексация"
async def send_file_upload_keyboard(update: Update):
    # Создаем кнопки "Загрузка файла" и "Переиндексация"
    upload_button = KeyboardButton("Загрузка файла")
    reindex_button = KeyboardButton("Переиндексация")
    # Создаем клавиатуру и добавляем на нее кнопки
    reply_keyboard = [[upload_button, reindex_button]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Отправляем клавиатуру пользователю
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

# Функция для выполнения bash-команды
def execute_bash_command(command):
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        result = process.stdout if process.stdout else process.stderr
        return result.strip()
    except Exception as e:
        return str(e)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    await send_file_upload_keyboard(update)

# Обработчик сообщений от пользователей
async def handle_message(update: Update, context: CallbackContext):
    global awaiting_password
    text = update.message.text
    print(f"User: {text}")

    # Если ожидается ввод пароля
    if awaiting_password:
        awaiting_password = False
        if text == INDEX_PASSWORD:
            if context.user_data.get('operation') == 'upload':
                # Загрузка файла
                await update.message.reply_text("Пожалуйста, отправьте HTML-файл.")
            elif context.user_data.get('operation') == 'reindex':
                # Запуск переиндексации
                await update.message.reply_text("Запуск переиндексации...")
                asyncio.create_task(run_reindex(update))
        else:
            await update.message.reply_text("Неверный пароль. Доступ запрещен.")
    else:
        # Проверяем, если текст соответствует кнопке "Загрузка файла" или "Переиндексация"
        if text == "Загрузка файла":
            context.user_data['operation'] = 'upload'
            await update.message.reply_text("Пожалуйста, отправьте HTML-файл.")
        elif text == "Переиндексация":
            context.user_data['operation'] = 'reindex'
            awaiting_password = True
            await update.message.reply_text("Введите пароль для выполнения операции:")
        else:
            # Пытаемся получить ответ несколько раз в случае ошибки
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = get_answer(text)
                    print(f'Bot: {response}')
                    await update.message.reply_text(response)
                    break  # Если успешно, выходим из цикла
                except Exception as e:
                    print(f'Error: {e}')
                    if attempt < max_retries - 1:
                        continue  # Пытаемся снова
                    else:
                        await update.message.reply_text("Произошла ошибка при обработке вашего запроса. Попробуйте позже.")

# Функция для выполнения переиндексации в фоновом режиме
def run_reindex_sync():
    script1_command = "python3 src/html_parser.py"
    script2_command = "python3 src/build_index.py"
    
    print(f"Выполнение: {script1_command}")
    script1_result = execute_bash_command(script1_command)
    if "ошибка" in script1_result.lower():
        script1_result = f"Ошибка при выполнении парсинга файлов: {script1_result}"
    else:
        script1_result = f"Парсинг файлов успешно завершен: {script1_result}"
    
    print(f"Выполнение: {script2_command}")
    script2_result = execute_bash_command(script2_command)
    if "ошибка" in script2_result.lower():
        script2_result = f"Ошибка при создании индекса: {script2_result}"
    else:
        script2_result = f"Создание индекса успешно завершено: {script2_result}"
    
    return script1_result, script2_result

async def run_reindex(update: Update):
    loop = asyncio.get_event_loop()
    script1_result, script2_result = await loop.run_in_executor(executor, run_reindex_sync)
    await update.message.reply_text(f"Результат выполнения первого скрипта:\n{script1_result}")
    await update.message.reply_text(f"Результат выполнения второго скрипта:\n{script2_result}")

# Обработчик загрузки файлов
async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document  # Получаем информацию о файле
    if file and file.file_name.endswith('.html'):  # Проверяем, что файл имеет расширение .html
        file_id = file.file_id  # Получаем идентификатор файла
        new_file = await context.bot.get_file(file_id)  # Получаем объект файла

        # Абсолютный путь для сохранения файла
        save_directory = '/home/vaa/.data_storage/projects/urfu_hackathon/data/html/downloaded_files'
        os.makedirs(save_directory, exist_ok=True)  #
        # Создаем каталог, если он не существует
        file_path = os.path.join(save_directory, file.file_name)  # Полный путь для сохранения файла
        file_bytes = await new_file.download_as_bytearray()  # Загружаем файл как байтовый массив
        with open(file_path, 'wb') as f:
            f.write(file_bytes)  # Сохраняем файл на сервере
        await update.message.reply_text(f'Файл сохранен как {file.file_name}')
    else:
        await update.message.reply_text('Пожалуйста, отправьте HTML-файл.')

# Обработчик ошибок
async def error(update: Update, context: CallbackContext):
    print(context.error)

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))  # Обработчик команды /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Добавляем обработчик документов
    app.add_error_handler(error)
    app.run_polling(poll_interval=1)
