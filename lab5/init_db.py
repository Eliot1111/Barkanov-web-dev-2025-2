# ~/Barkanov-web-dev-2025-2/init_db.py

from lab5.extensions import db
from lab5.models import User  # Импорт модели, чтобы таблицы точно создались
from lab5.app import app

with app.app_context():
    db.create_all()
