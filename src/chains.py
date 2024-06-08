import warnings

import torch
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from build_index import db

# Отключаем все предупреждения
warnings.filterwarnings("ignore")

# Создаем ретривер для поиска документов по схожести
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})

# Создаем менеджер коллбэков для обработки событий в процессе генерации
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Определяем правила для генерации ответа
system = """
Ты эксперт по базе знаний компании ПЭК. Пользователь задает тебе вопрос, ты отвечаешь на него в чате, используя только контекст базы знаний компании, предоставленной тебе в виде файлов. Твоя задача помочь 
пользователю найти ответ на вопрос, или решить его. Все ответы пиши в контексте процессов, регламентов и документов компании ПЭК. Пользователь это сотрудник компании, твоя задача максимально точно и понятно 
отвечать на вопросы пользователя. Помни, пользователь задает вопросы только в контексте базы знаний компании ПЭК. Отвечай только на заданный вопрос. Не делай повторов предложений. Отвечай так, чтобы 
пользователь мог самостоятельно решить свой вопрос, используя, приложение, документацию, или сайт компании. В ответе описывай шаги по решению вопроса, если оно есть в базе знаний. Не предлагай 
пользователю обращаться в техническую поддержку, ты и есть часть технической поддержки. То чего нет в базе знаний компании ты не знаешь, и ответить не можешь. Никогда не пиши вопрос решен, опиши шаги 
необходимые для решения вопроса.
"""

# Определяем шаблон запроса для использования в LLMChain
prompt_template = f"""
{system}
{{question}}
"""

# Создаем объект PromptTemplate с заданным шаблоном и входными переменными
PROMPT = PromptTemplate(template=prompt_template, input_variables=["question"])

# Определение устройства: CUDA если доступен, иначе CPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# Определение количества слоев для использования на GPU
n_gpu_layers = (
    -1 if device == "cuda" else 0
)  # -1 для максимального использования GPU, 0 для CPU

# Инициализируем модель LlamaCpp с заданными параметрами
llm = LlamaCpp(
    model_path="data/model/model-q8_0.gguf",  # Путь к модели
    temperature=0.1,  # Температура для управления степенью случайности в ответах
    max_tokens=512,  # Максимальное количество токенов в ответе
    max_length=1000,  # Максимальная длина текста (в символах)
    top_p=0.95,
    top_k=40,
    # callback_manager=callback_manager,  # Менеджер коллбэков
    f16_kv=True,
    n_batch=512,
    verbose=False,  # Отключение подробного вывода
    do_sample=True,
    repetition_penalty=1.9,
    return_full_text=True,
    max_new_tokens=400,  # Увеличиваем максимальное количество новых токенов
    n_ctx=4096,
    n_gpu_layers=n_gpu_layers,  # -1 для максимального использования GPU, 0 для CPU
    num_return_sequences=1,
)

# Создаем цепочки
llm_chain = PROMPT | llm | StrOutputParser()
rag_chain = {"context": retriever, "question": RunnablePassthrough()} | llm_chain


def get_answer(question):
    # Запускаем цепочку обработки вопроса и получаем ответ
    context_docs = retriever.get_relevant_documents(question)
    context = " ".join([doc.page_content for doc in context_docs])
    answer = llm_chain.invoke({"question": question, "context": context})
    relevant_docs = db.similarity_search(question, k=1)

    # Извлекаем уникальные источники и оставляем только нужную часть пути
    unique_sources = {
        "/".join(doc.metadata["source"].split("/")[-1:]) for doc in relevant_docs
    }
    sources_list = [f"{idx + 1}. {source}" for idx, source in enumerate(unique_sources)]
    sources = "\n".join(sources_list)

    # Формируем итоговый ответ с материалами
    answer_tmpl = f"""Ответ:{answer}\n\nМатериалы:\n{sources}"""
    return answer_tmpl


# Пример использования функции
if __name__ == "__main__":
    question = "Как быть если заказчик требует водителя с мед книжкой?"
    print(get_answer(question))
