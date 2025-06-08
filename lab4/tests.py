import pytest
from lab4.app import app, db
from lab4.models import User, Role
from werkzeug.security import generate_password_hash, check_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(
            login='admin',
            password_hash=generate_password_hash('Admin123!'),
            last_name='Админ',
            first_name='Система',
            patronymic=None,
            role_id=None
        )
        db.session.add(admin)
        db.session.commit()
    with app.test_client() as client:
        yield client

# Вспомогательные функции
def login_user(client, login, password):
    return client.post('/login', data={'login': login, 'password': password}, follow_redirects=True)

def logout_user(client):
    return client.get('/logout', follow_redirects=True)

# 1. Проверка доступа к главной странице

def test_index_accessible(client):
    rv = client.get('/')
    content = rv.data.decode('utf-8')
    assert 'Список пользователей' in content

# 2. Тест входа и выхода

def test_login_logout(client):
    rv = login_user(client, 'admin', 'Admin123!')
    assert 'успешно вошли' in rv.data.decode('utf-8') or 'успешно' in rv.data.decode('utf-8')
    rv = logout_user(client)
    assert 'Вход в систему' in rv.data.decode('utf-8')

# 3. Тест, что создание требует авторизации

def test_create_requires_login(client):
    rv = client.get('/user/create', follow_redirects=True)
    assert 'Вход в систему' in rv.data.decode('utf-8')

# 4. CRUD пользователя

def test_user_crud(client):
    # Логинимся
    login_user(client, 'admin', 'Admin123!')
    # Создаём роль
    with app.app_context():
        role = Role(name='TestRole', description='desc')
        db.session.add(role)
        db.session.commit()
        role_id = role.id

    # Создание
    rv = client.post('/user/create', data={
        'login': 'user1',
        'password': 'Password1!',
        'last_name': 'Иванов',
        'first_name': 'Иван',
        'patronymic': 'Иваныч',
        'role': str(role_id)
    }, follow_redirects=True)
    assert 'успешно создан' in rv.data.decode('utf-8')

    # Получаем созданного пользователя
    with app.app_context():
        user = User.query.filter_by(login='user1').first()
        assert user is not None
        uid = user.id

    # Просмотр
    rv = client.get(f'/user/{uid}')
    assert 'Иванов' in rv.data.decode('utf-8')
    assert 'TestRole' in rv.data.decode('utf-8')

    # Редактирование
    rv = client.post(f'/user/edit/{uid}', data={
        'last_name': 'Петров',
        'first_name': 'Пётр',
        'patronymic': '',
        'role': '0'
    }, follow_redirects=True)
    assert 'обновлены' in rv.data.decode('utf-8')

    rv = client.get(f'/user/{uid}')
    assert 'Петров' in rv.data.decode('utf-8')

    # Удаление
    rv = client.post(f'/user/delete/{uid}', follow_redirects=True)
    assert 'удалён' in rv.data.decode('utf-8')
    rv = client.get('/')
    assert 'user1' not in rv.data.decode('utf-8')

# 5. Смена пароля

def test_change_password(client):
    login_user(client, 'admin', 'Admin123!')
    # Неверный старый
    rv = client.post('/change-password', data={
        'old_password': 'wrong',
        'new_password': 'Newpass1!',
        'confirm': 'Newpass1!'
    }, follow_redirects=True)
    assert 'Старый пароль введён неверно' in rv.data.decode('utf-8')

    # Пароли не совпадают
    rv = client.post('/change-password', data={
        'old_password': 'Admin123!',
        'new_password': 'Newpass1!',
        'confirm': 'Mismatch1!'
    }, follow_redirects=True)
    assert 'Пароли не совпадают' in rv.data.decode('utf-8')

    # Успешная смена
    rv = client.post('/change-password', data={
        'old_password': 'Admin123!',
        'new_password': 'Newpass1!',
        'confirm': 'Newpass1!'
    }, follow_redirects=True)
    assert 'Пароль успешно изменён' in rv.data.decode('utf-8')

    logout_user(client)
    rv = login_user(client, 'admin', 'Newpass1!')
    assert 'успешно вошли' in rv.data.decode('utf-8')
