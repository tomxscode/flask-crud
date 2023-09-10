from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired
from wtforms import SubmitField

class formRegistro(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    enviarBtn = SubmitField('Enviar')

class formLogin(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    enviarBtn = SubmitField('Enviar')