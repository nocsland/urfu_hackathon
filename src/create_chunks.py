import re
import os
import pickle
from bs4 import BeautifulSoup, Tag
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document


dirname = os.path.dirname(os.path.dirname(__file__))

# Парсинг страницы в текст и удаление лишних символов
def html_to_text(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    strings = []

    title = soup.find(id ='title-text')
    if type(title) == Tag:
       title_text = title.get_text(strip=True)
       strings.append(title_text)

    content = soup.find(id ='content')  

    if type(content) == Tag:
      main_content = content.find(id='main-content')
      if type(main_content) == Tag:
        string = main_content.get_text(' ', strip=True)
        string = re.sub(r'\s+', ' ', string)
        string = re.sub(r'\n+', '\n', string)
        string = re.sub(r'\r+', '\r', string)
        string = re.sub(r'•+', ' ', string)
        if string != ' ' and string != '':
          strings.append(string)  


    full_text = '\n'.join(strings)
    return full_text


# Парсинг всех html документов и разбитие на чанки
def parse_html():
    dir = os.path.join(dirname, 'data/html')
    source_chunks = []
    splitter = CharacterTextSplitter(separator=" ",  chunk_size=4096, chunk_overlap=2048)

    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    html_content = f.read()
                    text = html_to_text(html_content)
                    for chunk in splitter.split_text(text):
                        source_chunks.append(Document(page_content=chunk, metadata={'source': file}))

    return source_chunks


# Парсинг страниц и сохранение чанков
if __name__ == '__main__':
    source_chunks = parse_html()
    
    filename = os.path.join(dirname, 'data/pkl/source_chunks.pkl')
    with open(filename, 'wb') as file:
        pickle.dump(source_chunks, file)
    print('Чанки созданы и сохранены')
    