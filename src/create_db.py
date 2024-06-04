import os
import pickle
import warnings
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Возьмем переменные окружения из .env
load_dotenv()

# Загружаем значене имени модели для эмбединов из файла .env
LL_MODEL = os.environ.get("LL_MODEL")


# Функциия создания векторной базы из чанков
def create_index_db(source_chunks):
    model_id = LL_MODEL
    # model_kwargs = {'device': 'cpu'}
    model_kwargs = {'device': 'cuda'}
    embeddings = HuggingFaceEmbeddings(
      model_name=model_id,
      model_kwargs=model_kwargs
    )

    db = FAISS.from_documents(source_chunks, embeddings)
    return db


# Создание и сохранение векторной базы
if __name__ == '__main__':    
    with open('../data/pkl/source_chunks.pkl', 'rb') as file:
        source_chunks = pickle.load(file)
    print('Чанки загружены')

    index_db = create_index_db(source_chunks)

    with open('../data/pkl/index_db.pkl', 'wb') as file:
        pickle.dump(index_db, file)    
    print('Векторная база создана и сохранена')