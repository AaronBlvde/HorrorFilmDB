from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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
    __tablename__ = 'movies'  # Имя вашей таблицы в базе данных
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))


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


# Ваш код для моделей Movie и User

# Функция для проверки, авторизован ли пользователь
def is_authenticated():
    return 'user_id' in session


# Функция для разлогинивания пользователя
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


# Маршрут для страницы входа
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


# Маршрут для страницы регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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


# Маршрут для личного кабинета
@app.route('/dashboard')
def dashboard():
    if is_authenticated():
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))


# Дополнительные маршруты и функции здесь

if __name__ == '__main__':
    app.run(debug=True)
