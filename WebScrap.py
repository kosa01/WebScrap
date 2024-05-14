from bs4 import BeautifulSoup
import requests
from openai import OpenAI


#WSTĘP-OPIS
#program pobiera artykuly ze strony UEP, chatbot według naszego polecenia przeprowadza selekcje na podstawie tytułow, dla tych artykułów które są zgodne z poleceniem(user_context), chat robi z tekstem to co chcemy (user_context_text) w tym wypadku skraca tekst do minimum i daje poezje o tekscie
#ze strony https://ue.poznan.pl/aktualnosci/ program pobiera tylko 9 artykułów gdyż strona jest dynamicznie zmieniana za pomocą js, a że biblioteka requests go nie obsluguje to są tylko 9
# problem ten znika jak strona jest podzielona na strony np. strona.pl/wiadomosci-1 strona.pl/wiadomosci-2
# wedlug upodoban można zmieniac zapytania do chat pgt(user_conent , user_content_text)
# aby chatbot zadzialal trzeba wkleic klucz api ktory znajduje sie w 16 linijce


#klucz udostępniający dostęp do openai
OPENAI_API_KEY = "TUTAJ KLUCZ API"
client = OpenAI(api_key=OPENAI_API_KEY)

#pobieranie artykułów z podanego linka
def scrape_articles(url_to_scrape):
    page_to_scrape = requests.get(url_to_scrape)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    elements = soup.findAll("div", class_="newsPreview__content")

    articles = []

    for index, element in enumerate(elements, start=1):
        if element.find('a'):
            link = element.find('a')['href']
        if element.find('time'):
            date = element.find('time').text.strip()
        if element.find('h3'):
            title = element.find('h3').text.strip()

        article_data = {
            "id": index,
            "link": link,
            "date": date,
            "title": title,
        }

        articles.append(article_data)
    return articles


def filter_articles(articles, numbers_list):
    articles_filtered = []

    for article in articles:
        if article["id"] in numbers_list:
            articles_filtered.append(article)

    return articles_filtered


#pobieranie przebranych artykułow i generowanie nowych przez AI
def read_articles(url_text,content2):

    page_to_scrape = requests.get(url_text)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    elements = soup.find("div", class_="textRich__content wysiwyg wysiwyg--liTick")
    final_data = chat_gpt(elements,content2)
    return final_data



# komunikacji z chatem gpt i generowania odpowiedzi
def chat_gpt(system_content, user_content):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # https://platform.openai.com/docs/models #gpt-4-turbo gpt-3.5-turbo
        messages=[
            {"role": "system", "content": f"{system_content}"},
            {"role": "user", "content": f"{user_content}"}
        ]
    )

    response = response = completion.choices[0].message.content.strip()

    return response


url_to_scrape = "https://ue.poznan.pl/studenci/komunikaty-dla-studentow/"
user_content = "twoim zadaniem jest wypisać numery id w słownikach, ważne jest to żebyś nie pisał nic oprócz tego(żadnych przecinków), Masz wypisywać numery id w których title odnosi się tylko i wyłącznie do : "
user_content_text = "twoim zadaniem jest przeanalizwoać tekst i zapisać w jak najkrótszej tresciwej formie, nie pisz zadnych rzeczy nie zwiazanych z tekstem, oraz dopisz cos zwiazanego na ten temat jako poezje"

user_content +=input("Podaj rzecz którą chcesz znaleźć w aktualnosciach UEP : ")
articles = scrape_articles(url_to_scrape)
articles_to_filter = chat_gpt(articles, user_content)
numbers_list = [int(num) for num in articles_to_filter.split() if num.isdigit()]
articles_to_read = filter_articles(articles,numbers_list)

for artile_to_read in articles_to_read:
    print("data :", artile_to_read["date"], "link :", artile_to_read["link"],"\n", read_articles(artile_to_read["link"], user_content_text),"\n")
