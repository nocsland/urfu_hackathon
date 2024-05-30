import warnings

from langchain.chains.llm import LLMChain
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from create_index import db

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Создаем ретривер для поиска документов по схожести
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})

# Создаем менеджер коллбэков для обработки событий в процессе генерации
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Определяем правила для генерации ответа
system = '''
Ты помощник по базе знаний компании ПЭК. Пользователь задает вопрос, ты отвечаешь на него, используя контекст из базы знаний компании.
Отвечай только на заданный пользователем вопрос. Не включай в ответ информацию, не относящуюся к вопросу.
Отвечай на вопрос в виде пошагового плана, основываясь на документах с материалами о внутренних процессах и регламентах компании. 
Предоставляй пользователю подробную информацию, чтобы он мог самостоятельно решить вопрос.
В ответе пиши ответ на вопрос, а не только ссылки на документы.
Описывай в ответе содержание документов отвечающих на вопрос пользователя.
'''

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
    model_path='data/model/saiga_mistral_7b.Q4_K_M.gguf',  # Путь к модели
    temperature=0.2,  # Температура для управления степенью случайности в ответах
    max_tokens=2000,  # Максимальное количество токенов в ответе
    max_length=512,  # Максимальная длина текста (в символах)
    top_p=0.95,
    top_k=50, 
    # callback_manager=callback_manager,  # Менеджер коллбэков
    f16_kv=True,
    n_batch=512,
    verbose=False,  # Отключение подробного вывода
    do_sample=True,
    repetition_penalty=1.1,
    return_full_text=True,
    max_new_tokens=400,
    n_ctx=4096,
    n_gpu_layers=-1, # закоментировать при работе с CPU
    num_return_sequences=1
)

# Создаем объект LLMChain с использованием модели и шаблона запроса
chain = LLMChain(prompt=PROMPT, llm=llm)

# Формулируем вопрос
question = 'Доступна ли перевозка грузов к Киргизию?'

# Создаем цепочки
llm_chain = PROMPT | llm | StrOutputParser()
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} | llm_chain
)
answer = rag_chain.invoke(question)
print(answer)
