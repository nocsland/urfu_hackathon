import os

from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters

from src2.chain_bot3 import rag_chain, db

# Загрузка переменных окружения из .env файла
load_dotenv()
# Чтение API-токена из переменной среды
TOKEN = os.getenv('BOT_API_TOKEN')


def get_answer(question):
    # Запускаем цепочку обработки вопроса и получаем ответ
    answer = rag_chain.invoke(question)
    relevant_docs = db.similarity_search(question, k=3)

    # Извлекаем уникальные источники и оставляем только нужную часть пути
    unique_sources = {"/".join(doc.metadata['source'].split('/')[-2:]) for doc in relevant_docs}
    sources_list = [f"{idx + 1}. {source}" for idx, source in enumerate(unique_sources)]
    sources = '\n'.join(sources_list)

    # Формируем итоговый ответ с материалами
    answer_tmpl = f"""Ответ:{answer}\n\nМатериалы:\n{sources}"""
    return answer_tmpl


async def handle_message(update, context):
    text = update.message.text
    print(f"User: {text}")

    response = get_answer(text)
    print(f'Bot: {response}')
    await update.message.reply_text(response)


async def error(update, context):
    print(context.error)


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    app.run_polling(poll_interval=1)
