import os
import pytest
from app import app

# Устанавливаем абсолютный путь к папке шаблонов
# Предполагается, что структура проекта: проект/tests/test_posts.py и проект/templates/
app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# 1. На странице "Параметры URL" отображаются переданные параметры
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

# 2. На странице "Заголовки запроса" отображаются заголовки запроса
def test_headers(client):
    response = client.get('/headers', headers={"X-Test-Header": "TestValue"})
    data = response.data.decode('utf-8')
    assert 'X-Test-Header' in data
    assert 'TestValue' in data

# 3. На странице "Cookie" корректно устанавливается куки
def test_cookie_set(client):
    response = client.get('/cookies')
    set_cookie = response.headers.get('Set-Cookie')
    assert set_cookie is not None and 'mycookie=cookie_value' in set_cookie
    data = response.data.decode('utf-8')
    assert 'не было установлено' in data

# 4. На странице "Cookie" корректно удаляется куки, если он уже был установлен
def test_cookie_delete(client):
    # Устанавливаем куки вручную; здесь set_cookie принимает ключ и значение
    client.set_cookie('localhost', 'mycookie', 'cookie_value')
    response = client.get('/cookies')
    set_cookie = response.headers.get('Set-Cookie')
    assert set_cookie is not None and 'mycookie=;' in set_cookie
    data = response.data.decode('utf-8')
    assert 'было установлено ранее' in data

# 5. На странице "Параметры формы" отображается форма (GET)
def test_form_data_get(client):
    response = client.get('/form_data')
    data = response.data.decode('utf-8')
    assert '<form method="post">' in data

# 6. На странице "Параметры формы" после отправки формы отображаются введённые данные
def test_form_data_post(client):
    response = client.post('/form_data', data={'data': 'test value'})
    data = response.data.decode('utf-8')
    assert 'test value' in data
    assert 'Полученные параметры формы' in data

# 7. Корректная валидация и форматирование номера: ввод с +7
def test_phone_valid_plus7(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-75-90'})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

# 8. Корректный ввод номера, начинающегося с 8
def test_phone_valid_8(client):
    response = client.post('/phone', data={'phone': '8(123)4567590'})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

# 9. Корректный ввод номера без префикса +7 или 8
def test_phone_valid_no_prefix(client):
    response = client.post('/phone', data={'phone': '123.456.75.90'})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data

# 10. Ошибка валидации: недопустимые символы в номере
def test_phone_invalid_characters(client):
    response = client.post('/phone', data={'phone': '123abc4567'})
    data = response.data.decode('utf-8')
    assert 'В номере телефона встречаются недопустимые символы' in data
    assert 'is-invalid' in data

# 11. Ошибка валидации: неверное количество цифр (без префикса)
def test_phone_invalid_digit_count(client):
    response = client.post('/phone', data={'phone': '123456789'})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

# 12. Ошибка валидации: неверное количество цифр для номера с +7
def test_phone_invalid_digit_count_plus7(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-75'})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

# 13. Валидация: пустой ввод
def test_phone_empty_input(client):
    response = client.post('/phone', data={'phone': ''})
    data = response.data.decode('utf-8')
    assert 'Неверное количество цифр' in data
    assert 'is-invalid' in data

# 14. При ошибке валидации выводится сообщение с классом Bootstrap
def test_phone_error_bootstrap_class(client):
    response = client.post('/phone', data={'phone': 'invalid#phone'})
    data = response.data.decode('utf-8')
    assert 'В номере телефона встречаются недопустимые символы' in data
    assert 'is-invalid' in data

# 15. Корректный ввод номера с дополнительными пробелами
def test_phone_valid_with_extra_spaces(client):
    response = client.post('/phone', data={'phone': '   +7 (123)   456-75-90   '})
    data = response.data.decode('utf-8')
    assert 'Недопустимый ввод' not in data
    assert '8-123-456-75-90' in data
