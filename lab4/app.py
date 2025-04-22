from flask import Flask, render_template, redirect, url_for, flash, request
from extensions import db, login_manager
from config import Config
from models import User, Role
from forms import UserForm, ChangePasswordForm
from auth import auth
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth)

# Создаем таблицы и дефолтного администратора при старте
with app.app_context():
    db.create_all()
    if not User.query.filter_by(login='admin').first():
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
        print('Default admin created: login=admin, password=Admin123!')

@app.route('/')
def index():
    users = User.query.order_by(User.id).all()
    return render_template('user_list.html', users=users)

@app.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_view.html', user=user)

@app.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()
    form.role.choices = [(0, 'Нет роли')] + [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        new_user = User(
            login=form.login.data,
            password_hash=generate_password_hash(form.password.data),
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data or None,
            role_id=form.role.data or None
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Пользователь успешно создан.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {e}', 'danger')
    return render_template('user_form.html', form=form, action='Создать')

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    # Убираем поля логина и пароля
    del form.login
    del form.password
    form.role.choices = [(0, 'Нет роли')] + [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.patronymic = form.patronymic.data or None
        user.role_id = form.role.data or None
        try:
            db.session.commit()
            flash('Данные пользователя обновлены.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении пользователя: {e}', 'danger')
    return render_template('user_form.html', form=form, action='Редактировать')

@app.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удалён.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {e}', 'danger')
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.old_password.data):
            flash('Старый пароль введён неверно.', 'danger')
        else:
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменён.', 'success')
            return redirect(url_for('index'))
    return render_template('change_password.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
