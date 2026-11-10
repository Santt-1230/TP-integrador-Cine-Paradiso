from flask import Blueprint, redirect, render_template, url_for, flash
import api

locales_bp = Blueprint('locales', __name__)

def sesion_invalida(error_api):
    return error_api.estado in (401, 403)

def redirigir_al_login():
    return redirect(url_for('usuarios.login'))

def redirigir_al_inicio():
    return redirect(url_for('peliculas_front.inicio'))

def leer_formulario(campos):
    datos = {}
    for campo in campos:
        datos[campo] = api.request.form.get(campo, '')
    return datos

def convertir_a_enteros(datos, campos):
    convertidos = dict(datos)
    for campo in campos:
        convertidos[campo] = int(datos[campo])
    return convertidos

def verificar_admin():
    if not api.session.get('id_usuario'):
        return redirigir_al_login()
    
    if api.session.get('rol') != 'administrador':
        flash('No tenes permisos para acceder a esta seccion', 'error')
        return redirect(url_for('peliculas_front.inicio'))

    return None

@locales_bp.app_context_processor
def inyectar_locales():
    locales = api.get_lista('/api/locales', 'locales')
    return {'locales':locales}

@locales_bp.route('/locales', methods = ['GET'])
def mostrar_locales():
    estado, datos_respuesta = api.get('/api/locales')
    if estado == 200:
        locales = datos_respuesta.get('locales', [])
        error = None
    else:
        locales = []
        error = api.mensaje_error(datos_respuesta)
    return render_template("locales.html", locales = locales, error = error)

@locales_bp.route('/elegir-cine/<int:id_local>', methods = ['GET'])
def elegir_cine(id_local):
    estado, datos_respuesta = api.get('/api/locales')

    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), 'error')
        return redirigir_al_inicio()
    locales = datos_respuesta.get('locales', [])
    local = None

    for local_actual in locales:
        if local_actual['id_local'] == id_local:
            local = local_actual

    if local is None:
        flash('El cine elegido no existe', 'error')
    else:
        api.session['cine_id'] = local['id_local']
        api.session['cine_nombre'] = local['nombre']
        
    return redirigir_al_inicio()
     

@locales_bp.route('/admin/locales', methods=['GET'])
def admin_locales():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    locales = []
    error = None
    salas_configuradas = 0
    estado, datos_respuesta = api.get('/api/locales')
    if estado == 401:
        return redirigir_al_login()
    if estado == 403:
        return redirigir_al_inicio()
    if estado != 200:
        error = api.mensaje_error(datos_respuesta)
    else:
        locales = datos_respuesta.get('locales', [])
        estado, datos_respuesta = api.get('/api/salas')
        if estado == 401:
            return redirigir_al_login()
        if estado == 403:
            return redirigir_al_inicio()
        if estado != 200:
            locales = []
        else:
            salas = datos_respuesta.get('salas', [])
            for local in locales:
                local['salas'] = []
                for sala in salas:
                    if sala['id_local'] == local['id_local']:
                        local['salas'].append(sala)
                local['total_butacas'] = sum(
                    sala['capacidad'] for sala in local['salas']
                )
            salas_configuradas = len(salas)
    
    return render_template("admin_locales.html", locales=locales,salas_configuradas=salas_configuradas, error=error)
