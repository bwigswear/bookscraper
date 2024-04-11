import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI

similar_books = []

class Book:
    def __init__(self, title='', author='', synopsis='', genres=None, url=''):
        self.title = title
        self.author = author
        self.synopsis = synopsis
        self.genres = genres if genres else []
        self.url = url

def get_book_url(title, author):
    search_url = f"https://www.goodreads.com/search?q={title}"
    response = requests.get(search_url)

    if response.status_code == 200:
        search_page = BeautifulSoup(response.content, 'html.parser')
        search_results = search_page.find_all('tr', {'itemtype': 'http://schema.org/Book'})

        for result in search_results:
            author_name = (result.find('a', {'class': 'authorName'})).find('span', {'itemprop': 'name'})
            print(author_name.string)
            if author.lower() == author_name.string.lower():
                return f"https://www.goodreads.com{result.find('a', class_='bookTitle')['href']}"
    else:
        print("Error retrieving search information")


def retrieve_book(url):
    
    if 'goodreads.com' in url.lower():
        response = requests.get(url)
    else:
        print("Not a GoodReads URL")
        return None

    if response.status_code == 200:
        book_page = BeautifulSoup(response.content, 'html.parser')
        book_title = book_page.find('h1', {'class': 'Text Text__title1'}).string
        book_author = book_page.find('span', {'class': 'ContributorLink__name'}).string
        book_synopsis = book_page.find('div', {'class': 'DetailsLayoutRightParagraph__widthConstrained'}).get_text(separator='\n', strip=True)
        genre_list = book_page.find('ul', {'class': 'CollapsableList'}).find_all('span', {'class': 'Button__labelItem'})
        book_genres = [genre.string for genre in genre_list if genre.string]
        book_genres = book_genres[:-1]
        book_url = url

        return Book(book_title, book_author, book_synopsis, book_genres, book_url)
        
    else:
        print("Error retrieving book information")

def compare_books(book1, book2): 
    #This function has not been tested since I don't want to buy API credits
    #WARNING: THIS FUNCTION WILL BE CALLED MANY TIMES AND WILL LIKELY USE MANY API CREDITS

    #Replacing this with environment variable is best practice
    client = OpenAI(api_key='Your Key Here')
    
    gpt_prompt = f"""
            Please compare the following two book synopsis and give me a similarity score on a scale of 1 to 10:
            
            Synopsis 1: {book1.synopsis}

            Synopsis 2: {book2.synopsis}


            """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": gpt_prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    response_text = response.choices[0].message['content'][0]['content']

    find_score = re.search(r"Similarity Score: (\d+\.\d+)/", response_text)

    if find_score:
        synopsis_similarity = float(find_score.group(1))
    else:
        print('Error retrieving Similarity Score from GPT response')

    #Current formula for comparison, nothing fancy
    return 0.5 * synopsis_similarity + 0.5 * (float(len(set(book1.genres).intersection(set(book2.genres)))))


def parse_related_lists(query_book):
    related_lists_url = f"https://www.goodreads.com/list/book/{re.search(r'show/(\d+)', query_book.url).group(1)}"
    response = requests.get(related_lists_url)

    if response.status_code == 200:
        related_list_page = BeautifulSoup(response.content, 'html.parser')
        list_urls = [rlist['href'] for rlist in related_list_page.find_all('a', {'class': 'listTitle'})]
    else:
        print("Error retrieving related list page")

    for url in list_urls:
        response = requests.get(f"https://www.goodreads.com/{url}")
        if response.status_code == 200:
            list_page = BeautifulSoup(response.content, 'html.parser')
            list_books = list_page.find_all('tr', {'itemtype': 'http://schema.org/Book'})

            for book in list_books: #This loop is untested since it relies on compare_books
                next_book = retrieve_book(f"https://www.goodreads.com/{book.find('a', {'itemprop': 'url'})['href']}")
                comparison_score = compare_books(query_book, next_book)
        
                if len(similar_books) < 10:
                    similar_books.push((next_book, comparison_score))
                    similar_books.sort(key=lambda x: x[1])
                else:
                    if comparison_score > similar_books[0][1]:
                        similar_books.pop(0)
                        similar_books.push(next_book, comparison_score)
                        similar_books.sort(key=lambda x: x[1])
                    

        else:
            print("Error retrieving related list page")
    #Now parse list_urls

def main():

    direct_url = input("If you have a direct GoodReads URL provide it, else type no: ")
    
    if direct_url.lower() != "no":
        query_book = retrieve_book(direct_url)
    else:
        query_title = input("What book are you interested in?: ")
        query_author = input("What is the author's name?: ")
        book_url = get_book_url(query_title, query_author)
        print(f"Using book URL: {book_url}")
        query_book = retrieve_book(book_url)

    parse_related_lists(query_book)

    print(similar_books)


if __name__ == "__main__":
    main()
