from flask import Flask, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

from datetime import datetime

import json

# forms
from forms.formTareas import formTarea
from forms.usuario import formRegistro, formLogin
from forms.formCategoria import formCategoria
from flask import url_for
from flask import request
from flask_login import login_user, current_user, UserMixin
from flask_login import logout_user

app = Flask(__name__)
app.secret_key = 'XXXXXXXXXXX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'

# configuración de flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

# otras funciones
def calcDiasRestantes(fecha_termino):
    fecha_actual = datetime.now().date()
    dias_restantes = (fecha_termino.date()) - fecha_actual
    return dias_restantes.days

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __init__(self, nombre, color, usuario_id):
        self.nombre = nombre
        self.color = color
        self.usuario_id = usuario_id
    
    def __repr__(self):
        return '<Categoria %r>' % self.nombre

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    fecha_termino = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)

    def __init__(self, titulo, descripcion, fecha_termino, usuario_id, categoria_id = None):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_termino = fecha_termino
        self.estado = False
        self.usuario_id = usuario_id
        self.categoria_id = categoria_id

    def __repr__(self):
        return '<Tarea %r>' % self.titulo

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Usuario %r>' % self.username
    
    def is_active(self):
        return True
    
def obtenerColorCategoria(idCategoria):
    categoria = Categoria.query.filter_by(id=idCategoria).first()
    return categoria.color

def obtenerNombreCategoria(idCategoria):
    categoria = Categoria.query.filter_by(id=idCategoria).first()
    return categoria.nombre

@app.route('/')
@login_required
def index():
    # funcionalidad para generar un gráfico
    # obtención de tareas
    tareas_completadas = Tarea.query.filter_by(usuario_id = current_user.id, estado=True).count()
    tareas_pendientes = Tarea.query.filter_by(usuario_id = current_user.id, estado=False).count()

    # datos para los gráficos
    labels = json.dumps(['Completadas', 'Pendientes'])
    datos = json.dumps([tareas_completadas, tareas_pendientes])

    return render_template('index.html', labels=labels, values=datos)

from routes.usuario import *
from routes.tareas import *
from routes.categorias import *

# iniciar el servidor flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)