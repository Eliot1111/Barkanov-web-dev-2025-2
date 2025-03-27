import os
import pytest
from app import app

# Если файл test_posts.py находится в корневой директории,
# а шаблоны – в папке templates, задаём путь к ним следующим образом:
app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# 1. Тесты для страницы "Параметры URL"
def test_url_params_with_parameters(client):
    response = client.get('/url_params?name=Test&value=123')
    data = response.data.decode('utf-8')
    assert 'name:' in data
    assert 'Test' in data
    assert 'value:' in data
    assert '123' in data

def test_url_params_no_parameters(client):
    response = client.get('/url_params')
    data = response.data.decode('utf-8')
    assert 'Параметры не переданы' in data

# 2. Тест для страницы "Заголовки запроса"
def test_headers(client):
    response = client.get('/headers', headers={"X-Test-Header": "TestValue"})
    data = response.data.decode('utf-8')
    assert 'X-Test-Header' in data
    assert 'TestValue' in data

def test_cookie_set(client):
    response = client.get('/cookies')
    set_cookie = response.headers.get('Set-Cookie')
    data = response.data.decode('utf-8')
    assert set_cookie is not None and 'mycookie=cookie_value' in set_cookie
    assert 'не было установлено' in data

def test_cookie_delete(client):
    client.set_cookie(domain='localhost', key='mycookie', value='cookie_value')
    response = client.get('/cookies')
    set_cookie = response.headers.get('Set-Cookie')
    data = response.data.decode('utf-8')
    assert set_cookie is not None and 'mycookie=;' in set_cookie
    assert 'было установлено ранее' in data


# 4. Тесты для страницы "Параметры формы"
def test_form_data_get(client):
    response = client.get('/form_data')
    data = response.data.decode('utf-8')
    assert '<form method="post">' in data

def test_form_data_post(client):
    response = client.post('/form_data', data={'data': 'test value'})
    data = response.data.decode('utf-8')
    assert 'test value' in data
    assert 'Полученные параметры формы' in data

# 5. Тесты для страницы проверки номера телефона

# Корректные варианты ввода:
def test_phone_valid_plus7(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-75-90'})
    data = response.data.decode('utf-8')
    # При корректном вводе ошибок не должно быть, а номер должен быть отформатирован
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

def test_phone_valid_8(client):
    response = client.post('/phone', data={'phone': '8(123)4567590'})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

def test_phone_valid_no_prefix(client):
    response = client.post('/phone', data={'phone': '123.456.75.90'})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

def test_phone_valid_with_extra_spaces(client):
    response = client.post('/phone', data={'phone': '   +7 (123)   456-75-90   '})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

# Обработка ошибок: неверный формат ввода
def test_phone_invalid_characters(client):
    response = client.post('/phone', data={'phone': '123abc4567'})
    data = response.data.decode('utf-8')
    assert 'В номере телефона встречаются недопустимые символы' in data
    assert 'is-invalid' in data

def test_phone_invalid_digit_count(client):
    response = client.post('/phone', data={'phone': '123456789'})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

def test_phone_invalid_digit_count_plus7(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-75'})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

def test_phone_empty_input(client):
    response = client.post('/phone', data={'phone': ''})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

def test_phone_error_bootstrap_class(client):
    response = client.post('/phone', data={'phone': 'invalid#phone'})
    data = response.data.decode('utf-8')
    assert 'В номере телефона встречаются недопустимые символы' in data
    assert 'is-invalid' in data
