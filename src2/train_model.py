import json
from langchain_core.documents import Document
from src2.chain_bot2 import PROMPT, retriever, llm


def train_model(retriever, training_data):
    """
    Функция для обучения ретривера на основе данных из JSON-файла.

    :param retriever: ретривер для доступа к базе данных
    :param training_data: путь к JSON-файлу с данными для обучения
    """
    with open(training_data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Извлекаем список документов из данных
    documents = [Document(question=item['question'], page_content=item['answer'], metadata={'source': item['source']}) for item in data]

    # Добавляем документы в ретривер
    retriever.add_documents(documents)


if __name__ == "__main__":
    # Путь к файлу с данными для обучения
    training_data_path = '../data/json/train_data.json'

    # Вызываем функцию обучения
    train_model(retriever, training_data_path)
