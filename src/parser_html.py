import pickle
import json
import warnings
import re

import spacy
from langchain_community.document_loaders import DirectoryLoader

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Загружаем исходные данные
loader = DirectoryLoader('../data/in/html')
docs = loader.load()

# Очищаем исходный текст
nlp = spacy.load('ru_core_news_sm')
for item in docs:
    doc = nlp(item.page_content)
    tokens = [
        str(token)  # .lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space]
    cleaned_text = ' '.join(tokens).strip()
    cleaned_text = re.sub(r'меток Обзор|Постоянная ссылка|Инструменты контента.*$', '', cleaned_text)
    cleaned_text = re.sub(r'^.*Переход началу метаданных', '', cleaned_text)
    item.page_content = cleaned_text

# Запись списка объектов в файл
with open('../data/in/pkl/cleared_documents.pkl', 'wb') as file:
    pickle.dump(docs, file)

# Преобразование объектов в словари для сохранения в JSON
docs_dicts = [item.__dict__ for item in docs]

# Запись списка словарей в файл JSON
with open('../data/out/json/cleared_documents.json', 'w', encoding='utf-8') as file:
    json.dump(docs_dicts, file, ensure_ascii=False, indent=4)
