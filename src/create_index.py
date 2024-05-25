# Чтение списка объектов из файла
import pickle
import re
import warnings

from joblib import Memory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Отключаем все предупреждения
warnings.filterwarnings("ignore")

with open('../data/in/pkl/cleared_documents.pkl', 'rb') as file:
    docs = pickle.load(file)

# Разделяем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=25)
source_chunks = splitter.split_documents(docs)

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


# Создаем функцию записи в базу данных FAISS
@memory.cache
def get_db():
    return FAISS.from_documents(source_chunks, embeddings)


# Записываем вектора
db = get_db()

# # Сохраняем индекс
db.save_local('../data/faiss_index')

topic = '"Какие документы необходимы"'
docs = db.similarity_search(topic, k=3)
message_content = re.sub(r'\n{2}', ' ', '\n '.join(
    [f'\n#### Релевантный фрагмент {i + 1} ####\n' + str(doc.metadata) + '\n' + doc.page_content + '\n' for i, doc in
     enumerate(docs)]))
print(message_content)
