from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired
from app import tables


class ShowTableForm(FlaskForm):
	table = RadioField('Укажите таблицу ', choices=tables)
	submit = SubmitField('Показать таблицу')


class LoginForm(FlaskForm):
	username = StringField('Введите логин: ', validators=[DataRequired()])
	password = PasswordField('Введите пароль: ', validators=[DataRequired()])
	remember_me = BooleanField("Запомнить меня", default=False)
	submit = SubmitField('Войти')