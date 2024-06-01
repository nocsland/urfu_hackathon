import os

from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters

from src2.chain_bot2 import rag_chain, llm, llm_chain

# Загрузка переменных окружения из .env файла
load_dotenv()
# Чтение API-токена из переменной среды
TOKEN = os.getenv('BOT_API_TOKEN')


async def handle_message(update, context):
    text = update.message.text
    print(f"User:{text}")

    response = rag_chain.invoke(text)
    print(f'Bot:{response}')
    await update.message.reply_text(response)


async def error(update, context):
    print(context.error)

    if __name__ == 'main':
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT, handle_message))
        app.add_error_handler(error)
        app.run_polling(poll_interval=1)
