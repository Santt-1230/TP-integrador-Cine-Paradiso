from flask import Blueprint, render_template, flash, request, redirect, url_for
import api

locales_bp = Blueprint('locales', __name__)

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


@locales_bp.route('/elegir-cine/<int:id_local>', methods=['GET'])
def elegir_cine(id_local):
    estado, datos_respuesta = api.get(f'/api/locales/{id_local}')

    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), 'error')
        return api.redirigir_al_inicio()

    local = datos_respuesta['local']

    api.session['cine_id'] = local['id_local']
    api.session['cine_nombre'] = local['nombre']

    pelicula_pendiente_id = api.session.pop('pelicula_pendiente_id', None)
    if pelicula_pendiente_id:
        return redirect(url_for(
            'peliculas_front.detalle',
            id_pelicula=pelicula_pendiente_id
        ))

    return api.redirigir_al_inicio()
     

@locales_bp.route('/admin/locales', methods=['GET'])
@api.admin_front_requerido
def admin_locales():
    params = {
        'estado': request.args.get('estado'),'local': request.args.get('local'),
    }

    estado, datos_respuesta = api.get('/api/locales/resumen-salas',params=params)

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

    return render_template(
        "admin_locales.html",
        locales=locales,
        todos_los_locales=todos_los_locales,
        salas_configuradas=salas_configuradas,
        error=error,
        filtro_estado=filtro_estado,
        filtro_local=filtro_local
    )
