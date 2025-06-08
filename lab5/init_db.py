import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lab5.extensions import db
from lab5.models import User
from lab5.app import app

with app.app_context():
    db.create_all()
