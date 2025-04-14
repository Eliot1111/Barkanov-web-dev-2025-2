import unittest
from app import app
from flask import session

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def login(self, username, password, remember='on'):
        return self.app.post('/login', data=dict(
            username=username,
            password=password,
            remember=remember
        ), follow_redirects=True)

    def test_visit_counter(self):
        with self.app as client:
            response = client.get('/counter')
            self.assertIn(b'Количество посещений', response.data)
            initial_visits = session.get('visits')
            response = client.get('/counter')
            self.assertEqual(session.get('visits'), initial_visits + 1)

    def test_successful_login(self):
        response = self.login('user', 'qwerty')
        self.assertIn(b'Вы успешно вошли в систему!', response.data)

    def test_unsuccessful_login(self):
        response = self.login('user', 'wrongpassword')
        self.assertIn(b'Неверно введён логин или пароль.', response.data)

    def test_access_secret_authenticated(self):
        self.login('user', 'qwerty')
        response = self.app.get('/secret')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Секретная страница', response.data)

    def test_access_secret_unauthenticated(self):
        response = self.app.get('/secret', follow_redirects=True)
        self.assertIn(b'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.', response.data)

    def test_redirect_to_secret_after_login(self):
        response = self.app.get('/secret', follow_redirects=True)
        self.assertIn(b'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.', response.data)
        response = self.app.post('/login?next=/secret', data=dict(
            username='user',
            password='qwerty',
            remember='on'
        ), follow_redirects=True)
        self.assertIn(b'Секретная страница', response.data)

    def test_remember_me_functionality(self):
        response = self.login('user', 'qwerty', remember='on')
        self.assertIn('remember_token', response.headers.get('Set-Cookie', ''))

    def test_navbar_links_authenticated(self):
        self.login('user', 'qwerty')
        response = self.app.get('/')
        self.assertIn(b'href="/secret"', response.data)

    def test_navbar_links_unauthenticated(self):
        response = self.app.get('/')
        self.assertNotIn(b'href="/secret"', response.data)

    def test_logout(self):
        self.login('user', 'qwerty')
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Вы вышли из системы.', response.data)

if __name__ == '__main__':
    unittest.main()
