from flask import Flask
from config import Config
from extensions import db, login_manager
from auth import auth_bp, check_rights
from logs import logs_bp, log_visit
from werkzeug.security import generate_password_hash
from flask import render_template
from models import User


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

with app.app_context():
    db.create_all()
    if not User.query.filter_by(login='admin').first():
        admin = User(
            login='admin',
            password=generate_password_hash('Admin123!'),
            role='Administrator',
            last_name='Иванов',
            first_name='Админ',
            patronymic='Система'
        )
        db.session.add(admin)
        db.session.commit()
        print('Администратор создан: admin / Admin123!')

app.register_blueprint(auth_bp)
app.register_blueprint(logs_bp, url_prefix='/logs')

@app.before_request
def before_all():
    return log_visit()


@app.route('/')
@check_rights(['Administrator', 'User'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
