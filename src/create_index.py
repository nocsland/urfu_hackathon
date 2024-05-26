# Чтение списка объектов из файла
import pickle
import warnings

from joblib import Memory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

with open('../data/in/pkl/cleared_documents.pkl', 'rb') as file:
    docs = pickle.load(file)

# Разделяем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=16384, chunk_overlap=0)
source_chunks = splitter.split_documents(docs)
print(source_chunks[9].page_content)

# Создаем эмбеддинги
model_id = 'sentence-transformers/all-MiniLM-L6-v2'
model_kwargs = {'device': 'cpu'}
embeddings = HuggingFaceEmbeddings(
    model_name=model_id,
    model_kwargs=model_kwargs
)

# Кэширование
cache_dir = '../cache'
memory = Memory(cache_dir)


# Функция по созданию индекса FAISS
# @memory.cache
def get_db():
    return FAISS.from_documents(source_chunks, embeddings)


# Сохраняем индекс в переменную
db = get_db()

# Сохраняем индекс в файл
db.save_local('../data/faiss_index')
