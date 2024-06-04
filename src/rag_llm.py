import re
import os
import openai
import pickle


# Загружаем векторную базу
dirname = os.path.dirname(os.path.dirname(__file__))
filename_index_db = os.path.join(dirname, 'data/pkl/index_db.pkl')
with open(filename_index_db, 'rb') as file:
    index_db = pickle.load(file)


# Функция поиска контекста по вопросу в векторной базе
def get_message_content(topic, index_db, k_num):
    # Поиск релевантных отрезков из базы знаний
    docs = index_db.similarity_search(topic, k = k_num)
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n#### Document excerpt №{i+1}####\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    sources = list(set(doc.metadata['source'] for doc in docs))
    sources = '\n'.join(sources)
    print(f"message_content={message_content}")
    return message_content, sources


# Функция подключения к API LLM и получения ответа
def answer_index(system, topic, message_content, temp):
    openai.api_type = "open_ai"
    openai.api_base = "http://localhost:5000/v1"
    openai.api_key = "no need anymore"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Here is the document with information to respond to the client: {message_content}\n\n Here is the client's question: \n{topic}"}
    ]

    completion = openai.ChatCompletion.create(
        model='no need anymore',
        messages=messages,
        temperature=temp
    )

    answer = completion.choices[0].message.content

    return answer


# Экспортируемая функция для использовании в боте (получения ответа и контекса)
def answer_user_question(topic):
    # Задание системного промпта
    system = 'Ты сотрудник поддержки компании занимающейся логистикой, тебя зовут пекGPT и ты отвечаешь на вопросы сотрудников в чате. У тебя есть документ со всеми материалами о внутренних процессах и регламентах. Ответь так, чтобы сотрудник решил свой вопрос. То чего нет в документе мы не можем это ответить. Не употребляй фразы вида “По нашему документу”, “в нашем документе”, “в документе с материалами”.'
    # Ищем реливантные вопросу чанки и формируем контент для модели, который будет подаваться в user
    message_content, sources = get_message_content(topic, index_db, k_num=5)
    # Делаем запрос в модель и получаем ответ модели
    answer = answer_index(system, topic, message_content, temp=0.1)
    answer = answer + '\n\n' + sources
    return answer, message_content

# Проверка функционала на тестовом вопросе
if __name__ == '__main__':
    topic ="Что делать, если клиент отказывается получения сопроводительных документов? "
    answer, message_content = answer_user_question(topic)
    print(f'answer={answer}')