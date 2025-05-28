import pytest
from app.models import db, Review, Course, User
from flask import url_for
from datetime import datetime


@pytest.fixture
def new_user(client, app):
    user = User(
        first_name='Иван',
        last_name='Иванов',
        middle_name='Иванович',
        login='ivan',
    )
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def new_course(app, new_user):
    course = Course(
        name='Тестовый курс',
        short_desc='Кратко',
        full_desc='Полное описание',
        category_id=1,
        author_id=new_user.id,
        background_image_id='test-img'
    )
    db.session.add(course)
    db.session.commit()
    return course


@pytest.fixture
def login(client, new_user):
    client.post('/auth/login', data={
        'login': 'ivan',
        'password': 'testpass'
    })
    return new_user


def test_create_review(client, app, login, new_course):
    response = client.post(
        f'/courses/{new_course.id}/reviews',
        data={'rating': '5', 'text': 'Отличный курс!'},
        follow_redirects=True
    )

    review = db.session.query(Review).filter_by(user_id=login.id, course_id=new_course.id).first()
    assert response.status_code == 200
    assert review is not None
    assert review.rating == 5
    assert review.text == 'Отличный курс!'


def test_update_review(client, app, login, new_course):
    # Первый отзыв
    client.post(f'/courses/{new_course.id}/reviews',
                data={'rating': '3', 'text': 'Нормально'},
                follow_redirects=True)

    # Обновление
    client.post(f'/courses/{new_course.id}/reviews',
                data={'rating': '1', 'text': 'Ужасно'},
                follow_redirects=True)

    review = db.session.query(Review).filter_by(user_id=login.id, course_id=new_course.id).first()
    assert review.rating == 1
    assert review.text == 'Ужасно'


def test_show_page_reviews(client, app, login, new_course):
    # Создать 6 отзывов
    for i in range(6):
        r = Review(
            course_id=new_course.id,
            user_id=login.id,
            rating=i % 5,
            text=f'Отзыв номер {i}',
            created_at=datetime.now()
        )
        db.session.add(r)
    db.session.commit()

    response = client.get(f'/courses/{new_course.id}')
    assert b'Отзывы о курсе' in response.data
    for i in range(1, 6):  # последние 5
        assert f'Отзыв номер {i}'.encode() in response.data


def test_all_reviews_page(client, app, login, new_course):
    # 10 отзывов от разных пользователей
    for i in range(10):
        user = User(
            first_name=f'Имя{i}',
            last_name='Тест',
            login=f'user{i}',
        )
        user.set_password('123')
        db.session.add(user)
        db.session.flush()
        r = Review(
            course_id=new_course.id,
            user_id=user.id,
            rating=(i % 6),
            text=f'Комментарий {i}',
            created_at=datetime.now()
        )
        db.session.add(r)
    db.session.commit()

    response = client.get(f'/courses/{new_course.id}/reviews')
    assert b'Отзывы о курсе' in response.data
    assert b'Комментарий 0' in response.data
    assert b'Комментарий 4' in response.data

    response_sorted = client.get(f'/courses/{new_course.id}/reviews?order=positive')
    assert response_sorted.status_code == 200
