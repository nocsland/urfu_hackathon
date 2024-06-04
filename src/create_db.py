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
    dirname = os.path.dirname(os.path.dirname(__file__))

    filename_source_chunks = os.path.join(dirname, 'data/pkl/source_chunks.pkl')
    with open(filename_source_chunks, 'rb') as file:
        source_chunks = pickle.load(file)
    print('Чанки загружены')

    index_db = create_index_db(source_chunks)

    filename_index_db = os.path.join(dirname, 'data/pkl/index_db.pkl')
    with open(filename_index_db, 'wb') as file:
        pickle.dump(index_db, file)    
    print('Векторная база создана и сохранена')