import warnings

import torch
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
Ты помощник по базе знаний компании ПЭК. Пользователь задает тебе вопрос, ты отвечаешь на него, используя только \
базу знаний компании. Предоставленные тебе файлы это база знаний компании.
Будь вежливым, если с тобой здороваются, поздоровайся в ответ. Спроси, чем ты можешь помочь пользователю.
Все ответы давай в контексте процессов, регламентов и документов компании ПЭК
Пользователь это сотрудник компании, твоя задача точно и подробно отвечать на вопросы пользователя. 
Отвечай только на заданный вопрос. Не включай в ответ информацию, не относящуюся к вопросу.
Предоставляй пользователю подробную информацию из базы знаний.
Сначала отвечай на вопрос. После этого опиши подробности ответа. 
Описывай конкретные шаги позволяющие пользователю получить ответ, или решить задачу. 
Если упоминаешь документ пиши его точное название.
Если в ответе перечисление действий, условий, или других сущностей, формируй их в виде списка.
Если тебя просят предоставить значения каких-либо данных, предоставляй именно значения.
Избегай повторов предложений в одном ответе. 
Отвечай на вопрос конкретно, используя характеристики, данные и точные значения
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

# Определение устройства: CUDA если доступен, иначе CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Определение количества слоев для использования на GPU
n_gpu_layers = -1 if device == 'cuda' else 0  # -1 для максимального использования GPU, 0 для CPU

# Инициализируем модель LlamaCpp с заданными параметрами
llm = LlamaCpp(
    model_path='../data/model/saiga_mistral_7b.Q4_K_M.gguf',  # Путь к модели
    temperature=0.1,  # Температура для управления степенью случайности в ответах
    max_tokens=2000,  # Максимальное количество токенов в ответе
    max_length=512,  # Максимальная длина текста (в символах)
    top_p=0.95,
    top_k=40,
    # callback_manager=callback_manager,  # Менеджер коллбэков
    f16_kv=True,
    n_batch=512,
    verbose=False,  # Отключение подробного вывода
    do_sample=True,
    repetition_penalty=1.2,
    return_full_text=True,
    max_new_tokens=400,
    n_ctx=8192,
    n_gpu_layers=n_gpu_layers,  # -1 для максимального использования GPU, 0 для CPU
    num_return_sequences=1
)

# Создаем объект LLMChain с использованием модели и шаблона запроса
chain = LLMChain(prompt=PROMPT, llm=llm)

# Создаем цепочки
llm_chain = PROMPT | llm | StrOutputParser()
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} | llm_chain
)


def get_answer(question):
    # Запускаем цепочку обработки вопроса и получаем ответ
    answer = rag_chain.invoke(question)
    relevant_docs = db.similarity_search(question, k=3)

    # Извлекаем уникальные источники и оставляем только нужную часть пути
    unique_sources = {"/".join(doc.metadata['source'].split('/')[-2:]) for doc in relevant_docs}
    sources_list = [f"{idx + 1}. {source}" for idx, source in enumerate(unique_sources)]
    sources = '\n'.join(sources_list)

    # Формируем итоговый ответ с материалами
    answer_tmpl = f"""Ответ:\n{answer}\n\nМатериалы:\n{sources}"""
    return answer_tmpl


# Пример использования функции
if __name__ == "__main__":
    question = 'Доступна ли перевозка грузов к Киргизию?'
    print(get_answer(question))
