import os

class Config:
    SECRET_KEY = 'super-secret-key-for-csrf'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:7004/vmshop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
