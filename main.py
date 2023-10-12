import requests
from bs4 import BeautifulSoup
import sqlite3

# Функция для создания базы данных
def create_database():
    conn = sqlite3.connect('horror_movies.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            rating TEXT,
            description TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция для вставки данных фильма в базу данных
def insert_movie(title, rating, description, image_url):
    conn = sqlite3.connect('horror_movies.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO movies (title, rating, description, image_url) VALUES (?, ?, ?, ?)',
                   (title, rating, description, image_url))
    conn.commit()
    conn.close()

# Функция для парсинга страницы с фильмами
def MovieScraper(start_page, end_page):
    for page_num in range(start_page, end_page + 1):
        url = f'https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&genres=horror&sort=user_rating,desc&start={page_num * 50}&ref_=adv_nxt&language=en'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers).content
        soup = BeautifulSoup(response, 'lxml')

        movie_details = soup.find_all('div', {'class': 'lister-item mode-advanced'})

        for movie in movie_details:
            movie_name = movie.find('h3', {'class': 'lister-item-header'}).text.replace('\n', '').strip()  # Убираем лишние символы и пробелы
            movie_name = movie_name.split('.', 1)[1].strip()  # Убираем индекс из строки
            movie_rating = movie.find('div', {'class': 'inline-block ratings-imdb-rating'}).text.strip()
            movie_describe = movie.find_all('p', class_='text-muted')[1].text
            img_url = imagescrapper(movie)

            insert_movie(movie_name, movie_rating, movie_describe, img_url)

# Функция для извлечения ссылки изображения фильма
def imagescrapper(movie):
    img_element = movie.find('img', class_='loadlate')
    if img_element:
        img_url = img_element['loadlate']
        return img_url
    else:
        return 'N/A'

# Создание бд
create_database()

# Парсинг страниц
MovieScraper(1, 2000)  # Здесь 2000 - это количество страниц (221,358 фильмов / 50 фильмов на страницу)
