import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, posts_list

def get_client():
    app.config['TESTING'] = True
    return app.test_client()

def test_index_status_code():
    client = get_client()
    response = client.get('/')
    assert response.status_code == 200

def test_index_content():
    client = get_client()
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert "Задание" in html

def test_posts_status_code():
    client = get_client()
    response = client.get('/posts')
    assert response.status_code == 200

def test_posts_content():
    client = get_client()
    response = client.get('/posts')
    html = response.data.decode('utf-8')
    assert "Последние посты" in html

def test_posts_data():
    client = get_client()
    response = client.get('/posts')
    html = response.data.decode('utf-8')
    first_post = posts_list[0]
    assert first_post['title'] in html

def test_post_valid_status_code():
    client = get_client()
    response = client.get('/posts/0')
    assert response.status_code == 200

def test_post_contains_comment_form():
    client = get_client()
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert "Оставьте комментарий" in html

def test_post_title_display():
    client = get_client()
    post = posts_list[0]
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert post['title'] in html

def test_post_text_display():
    client = get_client()
    post = posts_list[0]
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    snippet = post['text'][:30]
    assert snippet in html

def test_post_author_display():
    client = get_client()
    post = posts_list[0]
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert post['author'] in html

def test_post_date_format():
    client = get_client()
    post = posts_list[0]
    formatted_date = post['date'].strftime('%d.%m.%Y')
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert formatted_date in html

def test_post_image_included():
    client = get_client()
    post = posts_list[0]
    image_src = f"images/{post['image_id']}"
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert image_src in html

def test_post_comments_display():
    client = get_client()
    post = posts_list[0]
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    if post['comments']:
        comment = post['comments'][0]
        assert comment['author'] in html

def test_post_comment_placeholder():
    client = get_client()
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert "Введите ваш комментарий" in html

def test_nonexistent_post_returns_404():
    client = get_client()
    invalid_index = len(posts_list) + 1
    with pytest.raises(IndexError):
        client.get(f'/posts/{invalid_index}')
