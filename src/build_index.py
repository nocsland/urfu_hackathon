# Чтение списка объектов из файла
import pickle
import warnings

import torch
from joblib import Memory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

with open('data/pkl/cleared_documents.pkl', 'rb') as file:
    docs = pickle.load(file)

# Разделяем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=256)
source_chunks = splitter.split_documents(docs)

# Создаем эмбеддинги
# Определение устройства: CUDA если доступен, иначе CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Кэширование с отключением отладочной информации
cache_dir = 'cache'
memory = Memory(cache_dir, verbose=0)


# Функция по созданию индекса FAISS с использованием всех доступных видеокарт
@memory.cache
def get_db():
    # Создаем эмбеддинги с учетом всех доступных видеокарт
    model_id = 'intfloat/multilingual-e5-large'
    model_kwargs = {'device': device}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs=model_kwargs
    )

    return FAISS.from_documents(source_chunks, embeddings)


# Сохраняем индекс в переменную
db = get_db()

# Сохраняем индекс в файл
db.save_local('data/faiss_index')
