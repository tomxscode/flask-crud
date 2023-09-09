from flask import Flask, render_template, session, redirect

# forms
from forms.formTareas import formTarea
from flask import url_for

app = Flask(__name__)
app.secret_key = 'XXXXXXXXXXX'

# tareas
tareas = []
descripciones = []
fechas = []


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tarea/crear', methods=['POST', 'GET'])
def crearTarea():
    form = formTarea()
    if form.validate_on_submit():
        tareas.append(form.titulo.data)
        descripciones.append(form.descripcion.data)
        fechas.append(form.fecha_termino.data)
        session['exitoMsg'] = 'Tarea creada correctamente'
        if 'exitoMsg' in session:
            print("La variable de sesión exitoMsg está presente.")
        else:
            print("La variable de sesión exitoMsg no está presente.")
        print(tareas, descripciones, fechas)
    return render_template('crear_tarea.html', form=form)

# iniciar el servidor flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)