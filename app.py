from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from fuzzywuzzy import fuzz
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, HiddenField

app = Flask(__name__)
app._static_folder = 'static'
app.config.from_pyfile('config.py')
app.secret_key = 'your_secret_key'

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class CommentForm(FlaskForm):
    comment_text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    csrf_token = HiddenField()
    submit = SubmitField('Submit')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    csrf_token = HiddenField()
    submit = SubmitField('Submit')

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

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    text = db.Column(db.Text)
    user = db.relationship('User', backref='comments')
    movie = db.relationship('Movie', backref='comments')

def get_movies(page, per_page=50):
    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    return movies

def count_movies():
    return Movie.query.count()

def is_authenticated():
    return 'user_id' in session

@app.route('/')
def index():
    page = request.args.get('page', type=int, default=1)
    per_page = 50
    total_movies = count_movies()
    total_pages = (total_movies + per_page - 1) // per_page
    movies = get_movies(page, per_page)
    authenticated = is_authenticated()
    return render_template('index.html', movies=movies, page=page, total_pages=total_pages, is_authenticated=authenticated)

@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_details(movie_id):
    movie = Movie.query.get(movie_id)
    authenticated = is_authenticated()
    comments = Comment.query.filter_by(movie_id=movie_id).all()
    comment_form = CommentForm()

    if request.method == 'POST':
        if authenticated:
            user_id = session['user_id']
            text = comment_form.comment_text.data.strip()
            if text:
                comment = Comment(user_id=user_id, movie_id=movie_id, text=text)
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for('movie_details', movie_id=movie_id))
            else:
                flash('Введите комментарий', 'error')
        else:
            flash('Чтобы оставлять комментарии, необходимо войти.', 'error')

        action = request.form.get('action')
        if action == 'delete_comment':
            comment_id = int(request.form.get('comment_id'))
            comment = Comment.query.get(comment_id)
            if comment and comment.user_id == session['user_id']:
                db.session.delete(comment)
                db.session.commit()
                flash('Комментарий удален', 'success')
            else:
                flash('Вы не можете удалить этот комментарий', 'error')

    return render_template('movie_details.html', movie=movie, comments=comments, is_authenticated=authenticated, comment_form=comment_form)

from flask import request

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if is_authenticated():
        user_id = session['user_id']
        comment = Comment.query.get(comment_id)
        if comment and comment.user_id == user_id:
            db.session.delete(comment)
            db.session.commit()
            flash('Комментарий удален', 'success')
        else:
            flash('Вы не можете удалить этот комментарий', 'error')
    else:
        flash('Необходимо авторизоваться, чтобы удалить комментарий', 'error')

    # Перенаправьте пользователя на предыдущую страницу
    return redirect(request.referrer)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
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
                session['user_id'] = new_user.id
                return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/add_to_bookmarks/<int:movie_id>')
def add_to_bookmarks(movie_id):
    if is_authenticated():
        user_id = session['user_id']
        # Проверяем, есть ли уже такой фильм в закладках пользователя
        existing_bookmark = Bookmark.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing_bookmark:
            flash('Фильм уже добавлен в закладки.', 'error')
        else:
            bookmark = Bookmark(user_id=user_id, movie_id=movie_id)
            db.session.add(bookmark)
            db.session.commit()
            flash('Фильм добавлен в закладки.', 'success')
    else:
        flash('Необходимо авторизоваться, чтобы добавить фильм в закладки.', 'error')
    return redirect(url_for('index'))

@app.route('/bookmarks', methods=['GET', 'POST'])
def user_bookmarks():
    if is_authenticated():
        user_id = session['user_id']
        user = User.query.get(user_id)
        user_bookmarks = user.bookmarks
        bookmarked_movies = [bookmark.movie for bookmark in user_bookmarks]
        return render_template('dashboard.html', user=user, bookmarks=bookmarked_movies)
    else:
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if is_authenticated():
        user_id = session['user_id']
        user = User.query.get(user_id)
        bookmarks = user.bookmarks
        return render_template('dashboard.html', user=user, bookmarks=bookmarks)
    else:
        return redirect(url_for('login'))

def search_movies(query):
    query = query.strip().lower()
    all_movies = Movie.query.all()
    matching_movies = []
    for movie in all_movies:
        movie_title = movie.title.strip().lower()
        similarity = fuzz.partial_ratio(query, movie_title)
        if similarity > 70:
            matching_movies.append(movie)
    return matching_movies

@app.route('/remove_from_dashboard/<int:bookmark_id>', methods=['POST'])
def remove_from_dashboard(bookmark_id):
    if is_authenticated():
        # Получите информацию о закладке из базы данных и убедитесь, что она принадлежит текущему пользователю
        bookmark = Bookmark.query.get(bookmark_id)
        if bookmark and bookmark.user_id == session['user_id']:
            # Удалите закладку
            db.session.delete(bookmark)
            db.session.commit()
    return redirect(url_for('dashboard'))



@app.route('/search')
def search():
    query = request.args.get('query', '')
    movies = search_movies(query)
    return render_template('search_results.html', movies=movies, query=query)

if __name__ == '__main__':
    app.run(debug=True)
