from flask import render_template, session, redirect, flash, request, url_for
from flask_login import login_required, current_user
from app import app, db, Categoria, Tarea
from forms.formCategoria import formCategoria

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
    categoria = Categoria.query.get(id)
    if categoria.usuario_id != current_user.id:
        session['mensajeCustom'] = 'No tienes permiso para eliminar esta categoría'
        return redirect(url_for('verCategorias'))
    else:
        # Obteniendo la cantidad de tareas que tiene la categoría
        num_tareas = Tarea.obtenerCantTareasPorCategoria(categoria.id)
        if num_tareas > 0:
            # Si la cantidad de tareas es mayor a 0, no se puede eliminar la categoría
            session['mensajeCustom'] = 'No se puede eliminar esta categoría porque tiene tareas asociadas'
            return redirect(url_for('verCategoria', id=id))
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