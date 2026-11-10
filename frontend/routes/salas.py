from flask import Blueprint, redirect, session, render_template, request, url_for, flash
import api

salas_bp = Blueprint('salas', __name__)

CAMPOS_NUEVA_SALA = ['id_local', 'numero_sala', 'capacidad']
CAMPOS_EDITAR_SALA = ['numero_sala', 'estado']
CAMPOS_ENTEROS_SALA = ['numero_sala']


def redirigir_al_login():
    return redirect(url_for('usuarios.login'))

def redirigir_al_inicio():
    return redirect(url_for('peliculas_front.inicio'))

def leer_formulario(campos):
    datos = {}
    for campo in campos:
        datos[campo] = request.form.get(campo, '')
    return datos

def convertir_a_enteros(datos, campos):
    convertidos = dict(datos)
    for campo in campos:
        convertidos[campo] = int(datos[campo])
    return convertidos

def verificar_admin():
    if not session.get('id_usuario'):
        return redirigir_al_login()
    
    if session.get('rol') != 'administrador':
        flash('No tenes permisos para acceder a esta seccion.', 'error')
        return redirigir_al_inicio()

    return None

@salas_bp.route('/admin/salas/nueva', methods = ['GET', 'POST'])
def crear_sala():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta

    if request.method == 'GET':
        datos = {'id_local' : request.args.get('id_local', '')}
        return render_template('admin_editar_sala.html', datos=datos, id_sala=None, error=None)

    datos = leer_formulario(CAMPOS_NUEVA_SALA)
    error = None

    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_NUEVA_SALA)
        api.pedir('POST', f'/api/salas', datos_back)
        flash('La nueva sala se creo correctamente', 'success')
        return redirect(url_for('locales.admin_locales'))

    except ValueError:
        error = 'Completa todos los campos con números'

    except api.ApiError as error_api:
        if error_api.estado == 401:
            return redirigir_al_login()
        
        if error_api.estado == 403:
            return redirigir_al_inicio()
        
        error = error_api.mensaje

    return render_template('admin_editar_sala.html', datos=datos,id_sala=None, error=error )


@salas_bp.route('/admin/salas/<int:id_sala>/editar', methods = ['GET', 'POST'])
def editar_sala(id_sala):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    
    datos = {}
    error = None
    if request.method == 'GET':
        try:
            datos = api.pedir('GET', f'/api/salas/{id_sala}')['sala']

        except api.ApiError as error_api:
            if error_api.estado == 401:
                return redirigir_al_login()
                    
            if error_api.estado == 403:
                return redirigir_al_inicio()
            
            error = error_api.mensaje

        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    datos = leer_formulario(CAMPOS_EDITAR_SALA)
    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_ENTEROS_SALA)
        api.pedir('PATCH', f'/api/salas/{id_sala}', datos_back)
        flash('la sala se actualizó correctamente', 'success')
        return redirect(url_for('locales.admin_locales'))
    
    except ValueError:
        error = 'El numero de sala tiene que ser un numero'

    except api.ApiError as error_api:
        if error_api.estado == 401:
            return redirigir_al_login()
            
        if error_api.estado == 403:
            return redirigir_al_inicio()
            
        error = error_api.mensaje

    return render_template('admin_editar_sala.html', datos=datos, id_sala=id_sala, error=error)

@salas_bp.route('/admin/salas/<int:id_sala>/dar_baja', methods = ['POST'])
def desactivar_sala(id_sala):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    
    try:
        api.pedir('DELETE', f'/api/salas/{id_sala}')
        flash('La sala se dio de baja correctamente', 'success')

    except api.ApiError as error_api:
        if error_api.estado == 401:
            return redirigir_al_login()
                
        if error_api.estado == 403:
            return redirigir_al_inicio()
                
        flash(error_api.mensaje)

    return redirect(url_for('locales.admin_locales'))