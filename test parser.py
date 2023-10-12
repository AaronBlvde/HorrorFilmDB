import requests
from bs4 import BeautifulSoup

def MovieScraper(num):
    url = f'https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&genres=horror&sort=user_rating,desc&start={num}&ref_=adv_nxt&language=en'  # Добавляем параметр language=en
    print(url)
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'lxml')

    movie_details = soup.find_all('div', {'class': 'lister-item mode-advanced'})

    for movie in movie_details:
        movie_name = movie.find('h3', {'class': 'lister-item-header'}).text.replace('\n', '').strip()  # Убираем лишние символы и пробелы
        movie_rating = movie.find('div', {'class': 'inline-block ratings-imdb-rating'}).text.strip()
        movie_describe = movie.find_all('p', class_='text-muted')[1].text

        result_name = 'Movie Title: ' + movie_name + '\nRating: ' + movie_rating + '\nDescription:\n' + movie_describe

        img_url = imagescrapper(movie)

        print(result_name)
        print("Image URL:", img_url)
        print()

def imagescrapper(movie):
    img_element = movie.find('img', class_='loadlate')
    if img_element:
        img_url = img_element['loadlate']
        return img_url
    else:
        return 'N/A'

for page_num in range(5):
    MovieScraper(page_num * 50)

