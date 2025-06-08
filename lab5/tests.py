import pytest
from lab5.app import app, db
from lab5.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        admin = User(
            login='admin',
            password=generate_password_hash('adminpass'),
            last_name='Admin',
            first_name='User',
            patronymic='',
            role='Administrator'
        )
        db.session.add(admin)
        db.session.commit()

    with app.test_client() as client:
        yield client

    # Clean up
    with app.app_context():
        db.drop_all()

def login(client, username, password):
    return client.post('/login', data=dict(
        login=username,
        password=password
    ), follow_redirects=True)

def test_login_logout(client):
    rv = login(client, 'admin', 'adminpass')
    assert 'Вы вошли' in rv.data.decode('utf-8') or 'Logged in' in rv.data.decode('utf-8')
    rv = client.get('/logout', follow_redirects=True)
    assert 'Вы вышли' in rv.data.decode('utf-8') or 'Logged out' in rv.data.decode('utf-8')

def test_create_user(client):
    login(client, 'admin', 'adminpass')
    rv = client.post('/users/create', data=dict(
        login='newuser',
        password='newpass123',
        last_name='Test',
        first_name='User',
        patronymic='Testovich',
        role='User'
    ), follow_redirects=True)
    assert 'Пользователь создан' in rv.data.decode('utf-8') or 'User created' in rv.data.decode('utf-8')

def test_edit_user(client):
    login(client, 'admin', 'adminpass')
    user = User(
        login='edituser',
        password=generate_password_hash('editpass'),
        last_name='Old',
        first_name='Name',
        patronymic='',
        role='User'
    )
    db.session.add(user)
    db.session.commit()

    rv = client.post(f'/users/{user.id}/edit', data=dict(
        login='edituser',
        password='newpass456',
        last_name='New',
        first_name='Name',
        patronymic='Newovich',
        role='Administrator'
    ), follow_redirects=True)
    assert 'Пользователь обновлен' in rv.data.decode('utf-8') or 'User updated' in rv.data.decode('utf-8')

def test_delete_user(client):
    login(client, 'admin', 'adminpass')
    user = User(
        login='deluser',
        password=generate_password_hash('delpass'),
        last_name='Del',
        first_name='User',
        patronymic='',
        role='User'
    )
    db.session.add(user)
    db.session.commit()

    rv = client.post(f'/users/{user.id}/delete', follow_redirects=True)
    assert 'Пользователь удален' in rv.data.decode('utf-8') or 'User deleted' in rv.data.decode('utf-8')

def test_logs_page_access(client):
    login(client, 'admin', 'adminpass')
    rv = client.get('/logs/')
    assert rv.status_code == 200
    assert 'Журнал посещений' in rv.data.decode('utf-8') or 'Visit Log' in rv.data.decode('utf-8')

def test_export_pages_csv(client):
    login(client, 'admin', 'adminpass')
    rv = client.get('/logs/by-pages?export=csv')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/csv'
    assert 'page' in rv.data.decode('utf-8')

def test_export_users_csv(client):
    login(client, 'admin', 'adminpass')
    rv = client.get('/users?export=csv')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/csv'
    assert 'login' in rv.data.decode('utf-8')

def test_protected_page_requires_login(client):
    rv = client.get('/users', follow_redirects=True)
    assert 'Вход' in rv.data.decode('utf-8') or 'Login' in rv.data.decode('utf-8')
