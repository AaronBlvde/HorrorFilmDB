from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from fuzzywuzzy import fuzz


app = Flask(__name__)
app._static_folder = 'static'
app.config.from_pyfile('config.py')
app.secret_key = 'your_secret_key'  # Замените 'your_secret_key' на случайный секретный ключ


db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user = db.relationship('User', backref='bookmarks')
    movie = db.relationship('Movie', backref='bookmarks')

def get_movies(page, per_page=50):
    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    return movies

def count_movies():
    return Movie.query.count()

@app.route('/')
def index():
    page = request.args.get('page', type=int, default=1)
    per_page = 50
    total_movies = count_movies()
    total_pages = (total_movies + per_page - 1) // per_page
    movies = get_movies(page, per_page)

    # Устанавливаем переменную is_authenticated в True, если пользователь авторизован
    is_authenticated = 'user_id' in session

    return render_template('index.html', movies=movies, page=page, total_pages=total_pages,
                           is_authenticated=is_authenticated)
#Карточка фильма
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    # Здесь вам нужно получить информацию о фильме по его идентификатору (movie_id)
    movie = Movie.query.get(movie_id)

    # 'movie_details.html' для отображения подробной информации о фильме
    return render_template('movie_details.html', movie=movie)

# Функция для проверки, авторизован ли пользователь
def is_authenticated():
    return 'user_id' in session

# Функция для разлогинивания пользователя
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))  # Перенаправляем на главную страницу
        else:
            flash('Неверное имя пользователя или пароль')

    return render_template('login.html')

# Маршрут для страницы входа




    return render_template('login.html')

# Маршрут для страницы регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Пожалуйста, введите имя пользователя и пароль.')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Пользователь с таким именем уже существует.')
            else:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id  # Авторизуем пользователя сразу после регистрации
                return redirect(url_for('index'))  # Перенаправляем на главную страницу

    return render_template('register.html')




# Маршрут для добавления фильма в закладки
@app.route('/add_to_bookmarks/<int:movie_id>')
def add_to_bookmarks(movie_id):
    if is_authenticated():
        user_id = session['user_id']
        bookmark = Bookmark(user_id=user_id, movie_id=movie_id)
        db.session.add(bookmark)
        db.session.commit()
        flash('Фильм добавлен в закладки.', 'success')  # Добавляем "success" к flash сообщению
    else:
        flash('Необходимо авторизоваться, чтобы добавить фильм в закладки.', 'error')  # Добавляем "error" к flash сообщению
    return redirect(url_for('index'))

# Маршрут для просмотра закладок пользователя
@app.route('/bookmarks')
def bookmarks():
    if is_authenticated():
        user_id = session['user_id']
        user = User.query.get(user_id)
        user_bookmarks = user.bookmarks
        bookmarked_movies = [bookmark.movie for bookmark in user_bookmarks]
        return render_template('bookmarks.html', user=user, bookmarks=bookmarked_movies)
    else:
        return redirect(url_for('login'))

# Маршрут для личного кабинета
@app.route('/dashboard')
def dashboard():
    if is_authenticated():
        user_id = session['user_id']
        user = User.query.get(user_id)
        bookmarks = user.bookmarks  # Получаем все закладки пользователя
        return render_template('dashboard.html', user=user, bookmarks=bookmarks)
    else:
        return redirect(url_for('login'))

# Маршрут для удаления фильма из закладок
@app.route('/remove_from_bookmarks/<int:bookmark_id>', methods=['POST'])
def remove_from_bookmarks(bookmark_id):
    if is_authenticated():
        bookmark = Bookmark.query.get(bookmark_id)
        if bookmark and bookmark.user_id == session['user_id']:
            db.session.delete(bookmark)
            db.session.commit()
    return redirect(url_for('dashboard'))

#поиск фильма по названию в базе данных
def search_movies(query):
    query = query.strip().lower()

    # Получаем все фильмы из базы данных
    all_movies = Movie.query.all()

    # Создаем список для фильмов, которые подходят под критерии поиска
    matching_movies = []

    for movie in all_movies:
        movie_title = movie.title.strip().lower()

        # Используем библиотеку fuzzywuzzy для определения схожести строк
        similarity = fuzz.partial_ratio(query, movie_title)

        # Вы можете настроить порог схожести для определения, что считать подходящим
        if similarity > 70:  # Например, схожесть более 70%
            matching_movies.append(movie)

    return matching_movies
@app.route('/search')
def search():
    query = request.args.get('query', '')
    movies = search_movies(query)
    return render_template('search_results.html', movies=movies, query=query)


if __name__ == '__main__':
    app.run(debug=True)
