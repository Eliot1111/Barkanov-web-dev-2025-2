from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError, Email
from models import User

LOGIN_RE = r'^[A-Za-z0-9]{5,}$'
PWD_RE = r'^.{8,128}$'

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Regexp(LOGIN_RE, message='Только латинские буквы и цифры, не менее 5 символов')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class UserForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Regexp(LOGIN_RE, message='Только латинские буквы и цифры, не менее 5 символов')])
    password = PasswordField('Пароль', validators=[DataRequired(), Regexp(PWD_RE, message='Пароль должен быть 8–128 символов, без пробелов, содержать цифры и буквы')])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество')
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Роль')
    submit = SubmitField('Сохранить')

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Логин уже используется.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Regexp(PWD_RE, message='Пароль должен быть 8–128 символов, без пробелов, содержать цифры и буквы')])
    confirm = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('new_password', message='Пароли не совпадают')])
    submit = SubmitField('Изменить')