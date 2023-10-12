from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Функция для извлечения фильмов с учетом пагинации
def get_movies(page, per_page=50):
    conn = sqlite3.connect('database/horror_movies.db')
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    cursor.execute('SELECT title, rating, description, image_url FROM movies LIMIT ? OFFSET ?', (per_page, offset))
    movies = cursor.fetchall()
    conn.close()
    return movies

# Функция для определения общего количества фильмов
def count_movies():
    conn = sqlite3.connect('database/horror_movies.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM movies')
    count = cursor.fetchone()[0]
    conn.close()
    return count

@app.route('/')
def index():
    page = request.args.get('page', type=int, default=1)
    per_page = 50
    total_movies = count_movies()
    total_pages = (total_movies + per_page - 1) // per_page
    movies = get_movies(page, per_page)
    return render_template('index.html', movies=movies, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
