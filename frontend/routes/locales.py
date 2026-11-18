from flask import Blueprint, render_template, flash, request
import api

locales_bp = Blueprint('locales', __name__)

def sesion_invalida(error_api):
    return error_api.estado in (401, 403)


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
        return api.redirigir_al_inicio()
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
        
    return api.redirigir_al_inicio()
     

@locales_bp.route('/admin/locales', methods=['GET'])
@api.admin_front_requerido
def admin_locales():
    params = {
        'estado': request.args.get('estado'), 'id_local': request.args.get('local'),
    }
    
    estado, datos_respuesta = api.get('/api/salas', params=params)
    
    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    locales = []
    todos_los_locales = []
    salas_configuradas = 0
    filtro_estado = 'todas'
    filtro_local = None
    error = None

    if estado != 200:
        error = api.mensaje_error(datos_respuesta)
    else:
        locales = datos_respuesta.get('locales', [])
        todos_los_locales = datos_respuesta.get('todos_los_locales', [])
        salas_configuradas = datos_respuesta.get('salas_configuradas', 0)
        filtros = datos_respuesta.get('filtros', {})
        filtro_estado = filtros.get('estado', 'todas')
        filtro_local = filtros.get('id_local')

    return render_template("admin_locales.html",
                           locales=locales,
                           todos_los_locales=todos_los_locales,
                           salas_configuradas=salas_configuradas,
                           error=error,
                           filtro_estado=filtro_estado,
                           filtro_local=filtro_local)