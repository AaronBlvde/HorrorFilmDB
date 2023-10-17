import os

# Получите абсолютный путь к текущему каталогу
basedir = os.path.abspath(os.path.dirname(__file__))

# Укажите путь к базе данных как относительный путь от basedir к папке database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database/horror_movies.db')
