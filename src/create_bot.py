import warnings

from langchain.chains.llm import LLMChain
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from src.create_index import db

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Создаем ретривер для поиска документов по схожести
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 4})

# Создаем менеджер коллбэков для обработки событий в процессе генерации
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Определяем правила для генерации ответов
rules = """
1. При генерации ответа используйте данные из нашей базы знаний.
2. При генерации ответа учитывайте контекст вопроса.
3. Формулируйте ответы простым и понятным языком.
4. Ответы должны быть на русском языке.
"""

# Определяем шаблон запроса для использования в LLMChain
prompt_template = f"""
Правила:
{rules}

Вопрос:
    {{question}}    
Ответ:
    {{context}}
"""

# Создаем объект PromptTemplate с заданным шаблоном и входными переменными
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=['question', 'context']
)

# Инициализируем модель LlamaCpp с заданными параметрами
llm = LlamaCpp(
    model_path='../data/model/model-q4_K.gguf',  # Путь к модели
    temperature=0,  # Температура для управления степенью случайности в ответах
    max_tokens=2000,  # Максимальное количество токенов в ответе
    max_length=128,  # Максимальная длина текста (в символах)
    top_p=1,  # Параметр для управления вероятностным выбором токенов
    callback_manager=callback_manager,  # Менеджер коллбэков
    verbose=False,  # Отключение подробного вывода
)

# Создаем объект LLMChain с использованием модели и шаблона запроса
chain = LLMChain(llm=llm, prompt=PROMPT)

# Формулируем вопрос
question = 'Как осуществить Контроль выполнения НТМЦ?'

# Выполняем поиск похожих текстов в базе данных и получаем наиболее релевантный документ
relevants = db.similarity_search(question)
context = relevants[0].page_content  # Получаем содержимое первой страницы

# Запускаем цепочку обработки текста на основе выбранного документа и вопроса
print(chain.run({'context': context, 'question': question}))
