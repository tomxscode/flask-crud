from flask import render_template, session, redirect, flash, request, url_for
from flask_login import login_required, login_user, current_user, logout_user
import json
from datetime import datetime
from app import app, db, Usuario, login_manager
from forms.usuario import formRegistro, formLogin

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