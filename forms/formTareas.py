from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired
from wtforms import SubmitField

class formTarea(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descripcion = StringField('Descripcion', validators=[DataRequired()])
    fecha_termino = DateField('Fecha de termino', validators=[DataRequired()])
    enviarBtn = SubmitField('Enviar')