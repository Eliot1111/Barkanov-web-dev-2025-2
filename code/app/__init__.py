from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import auth_routes, main_routes, admin_routes, user_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(user_routes.bp)

    # Вызов инициализационной функции сразу при старте
    with app.app_context():
        check_create_admin_and_seed_data()

    return app

def check_create_admin_and_seed_data():
    from app.models import User, ConfTemplate

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print('✅ Администратор создан: username=admin, password=Admin123!')

    if ConfTemplate.query.count() == 0:
        templates = [
            ConfTemplate(
                name="Linux Basic",
                os="Linux",
                description="Начальный Linux сервер",
                photo="linux.png",
                cores=2,
                cpu_freq=2.5,
                gpu_cores=0,
                cuda=0,
                gpu_freq=0,
                ram_mem=4,
                ram_freq=2400,
                memory=50,
                price=10
            ),
            ConfTemplate(
                name="Windows Pro",
                os="Windows",
                description="Windows сервер для офисных задач",
                photo="windows.png",
                cores=4,
                cpu_freq=3.2,
                gpu_cores=1,
                cuda=256,
                gpu_freq=1200,
                ram_mem=8,
                ram_freq=2666,
                memory=100,
                price=20
            ),
            ConfTemplate(
                name="MacOS Dev",
                os="MacOS",
                description="MacOS для разработки",
                photo="apple.png",
                cores=8,
                cpu_freq=3.6,
                gpu_cores=2,
                cuda=512,
                gpu_freq=1500,
                ram_mem=16,
                ram_freq=3200,
                memory=200,
                price=30
            ),
            ConfTemplate(
                name="Linux Pro",
                os="Linux",
                description="Прокачанный Linux сервер",
                photo="linux.png",
                cores=16,
                cpu_freq=4.0,
                gpu_cores=4,
                cuda=1024,
                gpu_freq=2000,
                ram_mem=32,
                ram_freq=3600,
                memory=500,
                price=50
            )
        ]
        db.session.bulk_save_objects(templates)
        db.session.commit()
