from flask import Flask, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy

# forms
from forms.formTareas import formTarea
from flask import url_for
from flask import request

app = Flask(__name__)
app.secret_key = 'XXXXXXXXXXX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'

db = SQLAlchemy(app)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    fecha_termino = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Boolean, default=False)

    def __init__(self, titulo, descripcion, fecha_termino):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_termino = fecha_termino
        self.estado = False

    def __repr__(self):
        return '<Tarea %r>' % self.titulo

@app.route('/')
def index():
    return render_template('index.html')

# ruta de tareas, si se le pasa el valor id entonces mostrará un template, caso contrario, mostrará otro
@app.route('/tarea/', methods=['GET', 'POST'])
@app.route('/tarea/<int:id>', methods=['GET', 'POST'])
def verTareas(id=None):
    if id is None:
        tareas = Tarea.query.all()
        return render_template('tareas.html', tareas=tareas)
    else:
        tarea = Tarea.query.get(id)
        return render_template('tarea.html', tarea=tarea)

@app.route('/tarea/crear', methods=['POST', 'GET'])
def crearTarea():
    form = formTarea()
    if form.validate_on_submit():
        titulo = form.titulo.data
        descripcion = form.descripcion.data
        fecha_termino = form.fecha_termino.data
        db.session.add(Tarea(titulo, descripcion, fecha_termino))
        db.session.commit()
        session['mensajeCustom'] = 'Tarea creada correctamente'
        print(Tarea.query.all())
    return render_template('crear_tarea.html', form=form)

# métodos tareas
@app.route('/tarea/editar/estado/<int:id>', methods=['GET'])
def editarEstado(id):
    if request.method == 'GET':
        tarea = Tarea.query.get(id)
        tarea.estado = not tarea.estado
        db.session.commit()
        session['mensajeCustom'] = 'Estado modificado correctamente'
        return redirect(url_for('verTareas', id = id))
    
@app.route('/tarea/eliminar/<int:id>', methods=['GET'])
def eliminarTarea(id):
    if request.method == 'GET':
        tarea = Tarea.query.get(id)
        db.session.delete(tarea)
        db.session.commit()
        session['mensajeCustom'] = 'Tarea eliminada correctamente'
        return redirect(url_for('verTareas'))

# iniciar el servidor flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)