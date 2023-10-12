from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    return render_template('index.html', movies=movies, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
