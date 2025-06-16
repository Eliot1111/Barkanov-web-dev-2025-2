from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=45)])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Повторите пароль')
    submit = SubmitField('Зарегистрироваться')

class VMCreateForm(FlaskForm):
    cores = IntegerField('Cores', validators=[DataRequired()])
    cpu_freq = FloatField('CPU frequency', validators=[DataRequired()])
    gpu_cores = IntegerField('GPU cores', validators=[DataRequired()])
    cuda = IntegerField('CUDA', validators=[DataRequired()])
    gpu_freq = IntegerField('GPU frequency', validators=[DataRequired()])
    ram_mem = IntegerField('RAM memory', validators=[DataRequired()])
    ram_freq = IntegerField('RAM frequency', validators=[DataRequired()])
    memory = IntegerField('Memory', validators=[DataRequired()])
    submit = SubmitField('Добавить в корзину')


class ConfTemplateForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    os = StringField('ОС', validators=[DataRequired()])
    description = StringField('Описание')
    photo = StringField('Фото')
    cores = IntegerField('Ядра CPU', validators=[DataRequired()])
    cpu_freq = FloatField('Частота CPU', validators=[DataRequired()])
    gpu_cores = IntegerField('Ядра GPU')
    cuda = IntegerField('CUDA')
    gpu_freq = IntegerField('Частота GPU')
    ram_mem = IntegerField('RAM')
    ram_freq = IntegerField('Частота RAM')
    memory = IntegerField('Диск')
    price = IntegerField('Цена', validators=[DataRequired()])
    discount = IntegerField('Скидка (%)', validators=[NumberRange(min=0, max=100)], default=0)  # ➕
    submit = SubmitField('Создать шаблон')

