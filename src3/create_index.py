import pickle
import warnings

from joblib import Memory
from langchain.chains.llm import LLMChain
from langchain.retrievers import EnsembleRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

with open('data/in/pkl/cleared_documents.pkl', 'rb') as file:
    docs = pickle.load(file)

# Разделяем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=30)
source_chunks = splitter.split_documents(docs)

# Создаем эмбеддинги
model_id = 'sentence-transformers/all-MiniLM-L6-v2'
model_kwargs = {'device': 'cuda'} # При работе с CPU заменить на {'device': 'cpu'}
embeddings = HuggingFaceEmbeddings(
    model_name=model_id,
    model_kwargs=model_kwargs
)

# Кэширование
cache_dir = 'cache'
memory = Memory(cache_dir)

# Инициализируем ретриверы
bm25_retriever = BM25Retriever.from_documents(source_chunks)
bm25_retriever.k = 2
faiss_vectorstore = FAISS.from_documents(source_chunks, embeddings)
faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 2})

# Инициализируем ансамбль ретриверов
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
)
