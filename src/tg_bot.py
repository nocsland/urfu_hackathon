from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
import os
import rag_llm

# возьмем переменные окружения из .env
load_dotenv()

# загружаем значене токена из файла .env
TOKEN = os.environ.get("TOKEN")

# директория сохранения загруженных файлов
dirname = os.path.dirname(os.path.dirname(__file__))
DIR = os.path.join(dirname, 'data/html/')

# функция команды /start
async def start(update, context):
    keyboard = [['Начать', 'Перезапуск сервера', 'Загрузить файл']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Привет! Это бот пекGPT.\nГотов к работе.\nЗадайте ваш вопрос.', 
        reply_markup=reply_markup
    )

# функция для текстовых сообщений
async def text(update, context):
    if update.message.text == "Начать":
        reply_text = 'Для начала работы выполните команду /start'
    elif update.message.text == "Перезапуск сервера":
        reply_text = 'Для перезапуска сервера выполните команду /restart'
    elif update.message.text == "Загрузить файл":
        reply_text = 'Чтобы загрузить файл, просто перетащите его в диалог и нажмите отправить'
    else:
        # использование update
        print('-------------------')
        # print(f'update: {update}')
        print(f'date: {update.message.date}')
        print(f'id message: {update.message.message_id}')
        print(f'name: {update.message.from_user.first_name}')
        print(f'user.id: {update.message.from_user.id}')

        topic = update.message.text
        print(f'text: {topic}')

        chat_type = update.message.chat.type

        reply_text, gpt_message_content = rag_llm.answer_user_question(topic)


    await update.message.reply_text(f'{reply_text}')

    print(f'reply_text:\n{reply_text}')
    print('-------------------')


# основная функция запуска приложения телеграмм бота
def main():
    # точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен..!')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик команды /restart
    application.add_handler(CommandHandler('restart', restart))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # добавляем обработчик загруженных файлов
    application.add_handler(MessageHandler(filters.ATTACHMENT, upload))

    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()

    print('Бот остановлен..!')


# функция обработки загруженных файлов
async def upload(update, context):
    fileName = update.message.document.file_name

    if fileName.endswith('.html'):
        new_file = await update.message.effective_attachment.get_file()

        await new_file.download_to_drive(f'{DIR}{fileName}')
        await update.message.reply_text(
            f'Файл {fileName} успешно загружен!\n'
            'Введите /restart после загрузки всех файлов для применения обработки.'
        )
    else:
        await update.message.reply_text('Отправляемый файл должен быть с расширением .html')


# функция перезаргузки бота
async def restart(update, context):
    await update.message.reply_text(
        'Применение обработки данных занимает некоторое время.\n'
        'Идёт перезагрузка.\n'
        'Нажмите /start и ожидайте приветственного сообщения'
    )
    raise SystemExit()


if __name__ == "__main__":
    main()
