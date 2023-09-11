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

# manejo de login
@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = formLogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.usuario.data).first()
        if usuario and usuario.password == form.password.data:
            login_user(usuario)
            session['mensajeCustom'] = 'Bienvenido ' + usuario.username
            return redirect(url_for('verTareas'))
        else:
            session['mensajeCustom'] = 'Usuario o contraseña incorrectos'
    return render_template('login.html', form=form)

@app.route('/registro/', methods=['GET', 'POST'])
def registro():
    form = formRegistro()
    if form.validate_on_submit():
        # verificar si el usuario existe
        usuario_existente = Usuario.query.filter_by(username=form.usuario.data).first()
        if usuario_existente:
            session['mensajeCustom'] = 'El usuario ya existe'
        else:
            usuario = Usuario(form.usuario.data, form.email.data, form.password.data)
            db.session.add(usuario)
            db.session.commit()
            session['mensajeCustom'] = 'Usuario registrado'
            return redirect(url_for('login'))
    return render_template('registro.html', form=form)

@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    session['mensajeCustom'] = 'Hasta luego ' + current_user.username
    logout_user()
    return redirect(url_for('login'))

# ruta de tareas, si se le pasa el valor id entonces mostrará un template, caso contrario, mostrará otro
@app.route('/tarea/', methods=['GET', 'POST'])
@app.route('/tarea/<int:id>', methods=['GET', 'POST'])
@app.route('/tarea/filtrar/<estado>', methods=['GET', 'POST'])
@login_required
def verTareas(id=None, estado=None):
    # obtener el parámetro orden desde la url (get)
    orden = request.args.get('orden', 'asc')

    query = Tarea.query.filter_by(usuario_id=current_user.id)
    if estado is not None:
        if estado == "completadas":
            query = query.filter_by(estado=True)
        elif estado == "pendientes":
            query = query.filter_by(estado=False)
        else:
            session['mensajeCustom'] = 'Estado no válido'

    if id is None:
        if orden == 'asc':
            query = query.order_by(Tarea.fecha_termino.asc())
        elif orden == 'desc':
            query = query.order_by(Tarea.fecha_termino.desc())
        
        tareas = query.all()
        # agregando a tareas el color respectivo, con el campo "color":
        for tarea in tareas:
            if tarea.categoria_id is not None:
                tarea.color = obtenerColorCategoria(tarea.categoria_id)
                tarea.categoria_nombre = obtenerNombreCategoria(tarea.categoria_id)
        return render_template('tareas.html', tareas=tareas, calcDiasRestantes = calcDiasRestantes, orden=orden, estado=estado)
    else:
        tarea = Tarea.query.get(id)
        if tarea.categoria_id is not None:
            tarea.color = obtenerColorCategoria(tarea.categoria_id)
            tarea.categoria_nombre = obtenerNombreCategoria(tarea.categoria_id)
        dias_restantes = calcDiasRestantes(tarea.fecha_termino)
        if tarea.usuario_id != current_user.id:
            session['mensajeCustom'] = 'No tienes permiso para ver esta tarea'
            return redirect(url_for('verTareas'))
        return render_template('tarea.html', tarea=tarea, dias_restantes=dias_restantes)

@app.route('/tarea/crear', methods=['POST', 'GET'])
@login_required
def crearTarea():
    form = formTarea()
    # cargar las categorías desde la base de datos
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    # agregar la opción "sin categoría"
    form.categoria.choices = [('0', 'Sin categoría')]
    # agregar las categorías al formulario
    form.categoria.choices += [(categoria.id, categoria.nombre) for categoria in categorias]

    if form.validate_on_submit():
        titulo = form.titulo.data
        descripcion = form.descripcion.data
        fecha_termino = form.fecha_termino.data
        categoria = form.categoria.data
        if categoria == 0:
            db.session.add(Tarea(titulo, descripcion, fecha_termino, usuario_id=current_user.id))
        else:
            # TODO: validar que la categoría exista
            # TODO: validar que la categoría pertenezca al usuario
            db.session.add(Tarea(titulo, descripcion, fecha_termino, categoria_id=categoria, usuario_id=current_user.id))

        db.session.commit()
        session['mensajeCustom'] = 'Tarea creada correctamente'
        return redirect(url_for('verTareas'))
    return render_template('crear_tarea.html', form=form)

# métodos categorias
@app.route('/categoria/crear', methods=['POST', 'GET'])
@login_required
def crearCategoria():
    form = formCategoria()
    if form.validate_on_submit():
        nombre = form.nombre.data
        # comprobar si no hay una categoría con el mismo nombre del mismo usuario
        categoria_existente = Categoria.query.filter_by(nombre=nombre, usuario_id=current_user.id).first()
        if categoria_existente is not None:
            session['mensajeCustom'] = 'Ya existe una categoría con ese nombre'
            return redirect(url_for('crearCategoria'))
        color = form.color.data
        db.session.add(Categoria(nombre, color, current_user.id))
        db.session.commit()
        session['mensajeCustom'] = 'Categoría creada correctamente'
        # rederijir al usuario a la categoria creada
        return redirect(url_for('verCategoria', id=Categoria.query.filter_by(nombre=nombre, usuario_id=current_user.id).first().id))
    return render_template('crear_categoria.html', form=form)

@app.route('/categoria/eliminar/<int:id>', methods=['GET'])
@login_required
def eliminarCategoria(id):
    # TODO: eliminar las tareas de la categoría
    categoria = Categoria.query.get(id)
    if categoria.usuario_id != current_user.id:
        session['mensajeCustom'] = 'No tienes permiso para eliminar esta categoría'
        return redirect(url_for('verCategorias'))
    else:
        db.session.delete(categoria)
        db.session.commit()
        session['mensajeCustom'] = 'Categoría eliminada correctamente'
        return redirect(url_for('verCategoria'))

@app.route('/categoria/', methods=['GET'])
@app.route('/categoria/<int:id>', methods=['GET'])
@login_required
def verCategoria(id = None):
    if id is None:
        # mostrar todas las categorias
        categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
        return render_template('categorias.html', categorias=categorias)
    else:
        categoria = Categoria.query.get(id)
        if categoria.usuario_id != current_user.id:
            session['mensajeCustom'] = 'No tienes permiso para ver esta categoría'
            return redirect(url_for('verCategorias'))
        else:
            return render_template('categoria.html', categoria=categoria)
        
@app.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editarCategoria(id):
    categoria = Categoria.query.get(id)
    if categoria.usuario_id != current_user.id:
        session['mensajeCustom'] = 'No tienes permiso para editar esta categoría'
        return redirect(url_for('verCategorias'))
    if categoria is None:
        session['mensajeCustom'] = 'Categoría no encontrada'
        return redirect(url_for('verCategorias'))
    
    form = formCategoria(obj=categoria)
    if request.method == 'POST' and form.validate_on_submit():
        categoria.nombre = form.nombre.data
        categoria.color = form.color.data
        try:
            db.session.commit()
            session['mensajeCustom'] = 'Categoría modificada correctamente'
            return redirect(url_for('verCategoria', id=id))
        except Exception as e:
            db.session.rollback()
            session['mensajeCustom'] = f'Error al modificar la categoría{str(e)}'
    return render_template('editar_categoria.html', form=form)
        
# métodos tareas
@app.route('/tarea/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editarTarea(id):
    tarea = Tarea.query.get(id)
    if tarea.usuario_id != current_user.id:
        session['mensajeCustom'] = 'No tienes permiso para editar esta tarea'
        return redirect(url_for('verTareas'))
    if tarea is None:
        session['mensajeCustom'] = 'Tarea no encontrada'
        return redirect(url_for('verTareas'))

    form = formTarea(obj=tarea)
    # cargar las categorías desde la base de datos
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    # agregar la opción "sin categoría"
    form.categoria.choices = [('0', 'Sin categoría')]
    # agregar las categorías al formulario
    form.categoria.choices += [(categoria.id, categoria.nombre) for categoria in categorias]

    if request.method == 'POST' and form.validate_on_submit():
        tarea.titulo = form.titulo.data
        tarea.descripcion = form.descripcion.data
        tarea.fecha_termino = form.fecha_termino.data
        if form.categoria.data != 0:
            tarea.categoria_id = form.categoria.data
        elif form.categoria.data == 0:
            tarea.categoria_id = None
        try:
            db.session.commit()
            session['mensajeCustom'] = 'Tarea modificada correctamente'
            return redirect(url_for('verTareas', id=id))
        except Exception as e:
            db.session.rollback()
            session['mensajeCustom'] = f'Error al modificar la tarea{str(e)}'

    return render_template('editar_tarea.html', form=form, tarea=tarea)


@app.route('/tarea/editar/estado/<int:id>', methods=['GET'])
@login_required
def editarEstado(id):
    if request.method == 'GET':
        tarea = Tarea.query.get(id)
        if tarea.usuario_id != current_user.id:
            session['mensajeCustom'] = 'No tienes permiso para editar esta tarea'
            return redirect(url_for('verTareas'))
        tarea.estado = not tarea.estado
        db.session.commit()
        session['mensajeCustom'] = 'Estado modificado correctamente'
        return redirect(url_for('verTareas', id = id))
    
@app.route('/tarea/eliminar/<int:id>', methods=['GET'])
@login_required
def eliminarTarea(id):
    if request.method == 'GET':
        tarea = Tarea.query.get(id)
        if tarea.usuario_id != current_user.id:
            session['mensajeCustom'] = 'No tienes permiso para eliminar esta tarea'
            return redirect(url_for('verTareas'))
        db.session.delete(tarea)
        db.session.commit()
        session['mensajeCustom'] = 'Tarea eliminada correctamente'
        return redirect(url_for('verTareas'))

# iniciar el servidor flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)