import os

SECRET_KEY = 'secret-key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:qwerty123@localhost:8000/lab6'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'media', 
    'images'
)
