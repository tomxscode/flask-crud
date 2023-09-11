from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SelectField, SubmitField
class formCategoria(FlaskForm):
    choices = [('primary', 'Azul'), ('secondary', 'Verde'), ('success', 'Amarillo'), ('danger', 'Rojo'), ('warning', 'Naranja'), ('info', 'Azul claro'), ('light', 'Gris claro'), ('dark', 'Gris')]
    nombre = StringField('Nombre', validators=[DataRequired()])
    color = SelectField('Color', choices=choices)
    enviarBtn = SubmitField('Crear categoría')