from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from lab4.models import User
from lab4.extensions import db, login_manager
from lab4.forms import LoginForm, ChangePasswordForm

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash('Вы успешно вошли в систему.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Неверный логин или пароль.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('auth.login'))
