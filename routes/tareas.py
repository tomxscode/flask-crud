from flask import render_template, session, redirect, flash, request, url_for
from flask_login import login_required, current_user
import json
from app import app, db, Tarea, Categoria, calcDiasRestantes, obtenerColorCategoria, obtenerNombreCategoria, login_manager
from forms.formTareas import formTarea

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
            categoria_existe = Categoria.query.filter_by(id=categoria).first()
            if categoria_existe is None:
                session['mensajeCustom'] = 'La categoría no existe'
                return redirect(url_for('verTareas'))
            else:
                if categoria_existe.usuario_id != current_user.id:
                    session['mensajeCustom'] = 'No tienes permiso para crear esta tarea'
                    return redirect(url_for('verTareas'))
                else:
                    db.session.add(Tarea(titulo, descripcion, fecha_termino, categoria_id=categoria, usuario_id=current_user.id))
                    db.session.commit()
                    session['mensajeCustom'] = 'Tarea creada correctamente'
                    return redirect(url_for('verTareas'))
    return render_template('crear_tarea.html', form=form)

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
