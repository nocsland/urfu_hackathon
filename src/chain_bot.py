import warnings

from langchain.chains.llm import LLMChain
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from src.create_index import db

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Создаем ретривер для поиска документов по схожести
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})

# Создаем менеджер коллбэков для обработки событий в процессе генерации
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Определяем правила для генерации ответов
system = """
Ты помощник по базе знаний, пользователь задает вопрос, ты отвечаешь используя контекст из базы знаний.
В качестве базы знаний у тебя есть документ со всеми материалами о внутренних процессах и регламентах. 
Ответь так, чтобы пользователь решил свой вопрос.
"""

# Определяем шаблон запроса для использования в LLMChain
prompt_template = f"""
{system}

{{question}}

{{context}}
"""

# Создаем объект PromptTemplate с заданным шаблоном и входными переменными
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=['question', 'context']
)

# Инициализируем модель LlamaCpp с заданными параметрами
llm = LlamaCpp(
    model_path='../data/model/model-q4_K.gguf',  # Путь к модели
    temperature=0.1,  # Температура для управления степенью случайности в ответах
    max_tokens=2000,  # Максимальное количество токенов в ответе
    max_length=512,  # Максимальная длина текста (в символах)
    top_p=0.95,  # Параметр для управления вероятностным выбором токенов
    # callback_manager=callback_manager,  # Менеджер коллбэков
    f16_kv=True,
    n_batch=512,
    verbose=False,  # Отключение подробного вывода
    repetition_penalty=1.1,
    return_full_text=True,
    max_new_tokens=400,
    n_ctx=4096

)

# Создаем объект LLMChain с использованием модели и шаблона запроса
chain = LLMChain(prompt=PROMPT, llm=llm)

# Формулируем вопрос
question = 'Как быть если заказчик требует водителя с мед книжкой?'

# Выполняем поиск похожих текстов в базе данных и получаем наиболее релевантный документ
relevants = db.similarity_search(question)
context = relevants[0].page_content  # Получаем содержимое первой страницы
# context = " ".join([item.page_content for item in relevants])

# Получаем исходный файл
source = relevants[0].metadata['source'].split('/')[-1]

# Запускаем цепочку обработки текста на основе выбранного документа и вопроса
result = chain.invoke({'question': question, 'context': context})

answer = f"""
Вопрос:
    {result['question']}
Ответ:
    {(result['text'])}

Материалы:
    {source}
"""

print(answer)
