import warnings

from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from create_index import ensemble_retriever

# Отключаем все предупреждения
warnings.filterwarnings('ignore')

# Формулируем вопрос
question = 'Что входит в доставку в гипермаркеты?'
docs = ensemble_retriever.invoke(question)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Определяем правила для генерации ответов
system = """
Ты помощник по базе знаний, пользователь задает вопрос, ты отвечаешь на него, 
используя контекст из базы знаний. В качестве базы знаний у тебя документ со всеми материалами о внутренних 
процессах и регламентах компании. В ответе описывай конкретные шаги и названия документов, ведущие к тому, чтобы 
пользователь получил ответ на свой вопрос. 
"""

# Определяем шаблон запроса для использования в LLMChain
prompt_template = f"""
{system}

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
    model_path='data/model/saiga_mistral_7b.Q4_K_M.gguf',  # Путь к модели
    temperature=0.1,  # Температура для управления степенью случайности в ответах
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

llm_chain = PROMPT | llm | StrOutputParser()

rag_chain = (
        {"context": ensemble_retriever, "question": RunnablePassthrough()} | llm_chain
)

result = rag_chain.invoke(question)
print(result)
