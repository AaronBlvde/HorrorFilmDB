import sqlite3


def view_movies():
    conn = sqlite3.connect('horror_movies.db')
    cursor = conn.cursor()

    # Используем SQL-запрос COUNT(*) для подсчета количества строк
    cursor.execute('SELECT COUNT(*) FROM movies')
    count = cursor.fetchone()[0]  # Извлекаем значение COUNT(*)

    print("Total Records:", count)

    # Выполняем SQL-запрос для извлечения данных о фильмах
    cursor.execute('SELECT title, rating, description, image_url FROM movies')
    records = cursor.fetchall()

    conn.close()

    for record in records:
        print("Title:", record[0])
        print("Rating:", record[1])
        print("Description:", record[2])
        print("Image URL:", record[3])
        print()


view_movies()
