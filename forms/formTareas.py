from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired
from wtforms import SubmitField

class formTarea(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descripcion = StringField('Descripcion', validators=[DataRequired()])
    fecha_termino = DateField('Fecha de termino', validators=[DataRequired()])
    categoria = SelectField('Categoria', coerce=int)
    enviarBtn = SubmitField('Enviar')