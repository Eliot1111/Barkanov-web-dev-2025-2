from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from forms import LoginForm, UserForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_rights(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed_roles:
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
@check_rights(['Administrator'])
def list_users():
    users = User.query.all()
    return render_template('users/list.html', users=users)


@auth_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@check_rights(['Administrator'])
def create_user():
    form = UserForm()
    form.role.choices = [('User', 'Пользователь'), ('Administrator', 'Администратор')]

    if form.validate_on_submit():
        user = User(
            login=form.login.data,
            password=generate_password_hash(form.password.data),
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data,
            role=form.role.data,
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Пользователь создан.', 'success')
        return redirect(url_for('auth.list_users'))
    else:
        print(form.errors)
    return render_template('users/form.html', form=form, action='Создать')


@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights(['Administrator'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    form.role.choices = [('User', 'Пользователь'), ('Administrator', 'Администратор')]

    if form.validate_on_submit():
        user.login = form.login.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.patronymic = form.patronymic.data
        user.role = form.role.data
        db.session.commit()
        flash('Пользователь обновлён.', 'success')
        return redirect(url_for('auth.list_users'))

    return render_template('users/form.html', form=form, action='Редактировать')


@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights(['Administrator'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален.', 'success')
    return redirect(url_for('auth.list_users'))

@auth_bp.route('/users/<int:user_id>')
@login_required
@check_rights(['Administrator', 'User'])
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 'User' and current_user.id != user.id:
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('index'))
    return render_template('users/profile.html', user=user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.old_password.data):
            flash('Старый пароль неверный.', 'danger')
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Пароль изменён.', 'success')
            return redirect(url_for('index'))
    return render_template('change_password.html', form=form)
