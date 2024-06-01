import json
import pickle
import re
import warnings

import spacy
from langchain_community.document_loaders import DirectoryLoader

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Загружаем исходные данные
loader = DirectoryLoader('../data/html')
docs = loader.load()

# Очищаем исходный текст
nlp = spacy.load('ru_core_news_sm')
for item in docs:
    doc = nlp(item.page_content)
    tokens = [
        str(token)  # .lemma_
        for token in doc
        if not token.is_space]
    cleaned_text = ' '.join(tokens).strip()
    cleaned_text = re.sub(
        r'Нет меток Обзор.*|Обзор Инструменты.*|Написать комментарий.*|Инструменты контента.*|фт контента.*| ОЦЕНОЧНАЯ.*',
        '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'(= ?)+', '', cleaned_text)
    cleaned_text = re.sub(r'^.*Переход к началу метаданных', '', cleaned_text)
    item.page_content = cleaned_text

# Запись списка объектов в файл
with open('../data/pkl/cleared_documents.pkl', 'wb') as file:
    pickle.dump(docs, file)

# Преобразование объектов в словари для сохранения в JSON
docs_dicts = [item.__dict__ for item in docs]

# Запись списка словарей в файл JSON
with open('../data/json/cleared_documents.json', 'w', encoding='utf-8') as file:
    json.dump(docs_dicts, file, ensure_ascii=False, indent=4)
