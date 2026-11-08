from flask import Blueprint, redirect, session, render_template, request, url_for
import api

locales_bp = Blueprint('locales', __name__)

@locales_bp.app_context_processor
def inyectar_locales():
    try:
        locales = api.get_lista('/api/locales', 'locales')
    except api.ApiError:
        locales = []
    return {'locales':locales}

@locales_bp.route('/locales', methods = ['GET'])
def mostrar_locales():
    try:
        locales = api.get_lista('/api/locales', 'locales')
        error = None
    except api.ApiError as error_api:
        locales = []
        error = error_api.mensaje
    return render_template("locales.html", locales = locales, error = error)

@locales_bp.route('/elegir-cine/<int:id_local>', methods = ['GET'])
def elegir_cine(id_local):
    locales = []
    local = None
    error = None
    try:
        locales = api.get_lista('/api/locales', 'locales')

        for local_actual in locales:
            if local_actual['id_local'] == id_local:
                local = local_actual

        if local is None:
            error = "El cine elegido no existe"

    except api.ApiError as error_api:
        error = error_api.mensaje

    if error is None:
        session['cine_id'] = local['id_local']
        session['cine_nombre'] = local['nombre']
        
    return redirect('/')
     

@locales_bp.route('/admin/locales', methods=['GET'])
def admin_locales():
    locales = []
    error = None

    try:
        locales = api.get_lista('/api/locales', 'locales')
        salas = api.pedir('GET', '/api/salas')['salas']
        for local in locales:
            local['salas'] = []
            for sala in salas:
                if sala['id_local'] == local['id_local']:
                    local['salas'].append(sala)
        
    except api.ApiError as error_api:
        if error_api.estado in (401, 403):
            return redirect(url_for('usuarios.login'))
        locales = []
        error = error_api.mensaje
    return render_template("admin_locales.html", locales=locales, error=error)
