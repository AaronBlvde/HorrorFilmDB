1. Создайте виртуальную среду Python (если она еще не создана):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate  # Для Windows
   
pip install -r requirements.txt

Инициализируйте базу данных и примените миграции:
flask db init
flask db migrate -m "Начальное состояние базы данных"
flask db upgrade

python app.py
