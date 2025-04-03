from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации."

users = {
    'user': {
        'password': 'qwerty'
    }
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
def index():
    message = ""
    if current_user.is_authenticated:
        message = "Вы успешно вошли в систему!"
    return render_template('index.html', message=message)

@app.route('/counter')
def counter():
    session['visits'] = session.get('visits', 0) + 1
    return render_template('counter.html', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         remember = True if request.form.get('remember') == 'on' else False
         if username in users and users[username]['password'] == password:
             user = User(username)
             login_user(user, remember=remember)
             flash("Вы успешно вошли в систему!", "success")
             next_page = request.args.get('next')
             return redirect(next_page or url_for('index'))
         else:
             flash("Неверно введён логин или пароль.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

if __name__ == '__main__':
    app.run(debug=True)
