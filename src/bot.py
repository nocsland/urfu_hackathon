import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
from main import get_answer

# Загрузка переменных окружения из .env файла
load_dotenv()
# Чтение API-токена из переменной среды
TOKEN = os.getenv('BOT_API_TOKEN')

# Функция для отправки клавиатуры "Загрузка файла"
async def send_file_upload_keyboard(update: Update):
    # Создаем кнопку "Загрузка файла"
    button_text = "Загрузка файла"
    button = KeyboardButton(button_text)
    # Создаем клавиатуру и добавляем на нее кнопку
    reply_keyboard = [[button]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Отправляем клавиатуру пользователю
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

# Обработчик сообщений от пользователей
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    print(f"User: {text}")
    # Проверяем, если текст соответствует кнопке "Загрузка файла"
    if text == "Загрузка файла":
        await send_file_upload_keyboard(update)  # Отправляем клавиатуру "Загрузка файла"
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

# Обработчик загрузки файлов
async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document  # Получаем информацию о файле
    if file and file.file_name.endswith('.html'):  # Проверяем, что файл имеет расширение .html
        file_id = file.file_id  # Получаем идентификатор файла
        new_file = await context.bot.get_file(file_id)  # Получаем объект файла

        # Абсолютный путь для сохранения файла
        save_directory = '/home/vaa/.data_storage/projects/urfu_hackathon/data/html/downloaded_files'
        os.makedirs(save_directory, exist_ok=True)  # Создаем каталог, если он не существует

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Добавляем обработчик документов
    app.add_error_handler(error)
    app.run_polling(poll_interval=1)
