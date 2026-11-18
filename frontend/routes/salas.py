from flask import Blueprint, redirect, render_template, url_for, request
import api

salas_bp = Blueprint('salas', __name__)

CAMPOS_NUEVA_SALA = ['id_local', 'numero_sala', 'capacidad']
CAMPOS_EDITAR_SALA = ['numero_sala', 'estado', 'capacidad']
CAMPOS_ENTEROS_SALA = ['numero_sala', 'capacidad']


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

@salas_bp.route('/admin/salas/nueva', methods = ['GET', 'POST'])
@api.admin_front_requerido
def crear_sala():
    if request.method == 'GET':
        datos = {'id_local' : request.args.get('id_local', '')}
        return render_template('admin_editar_sala.html', datos=datos, id_sala=None, error=None)

    datos = leer_formulario(CAMPOS_NUEVA_SALA)

    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_NUEVA_SALA)
    except ValueError:
        return render_template('admin_editar_sala.html', datos=datos,id_sala=None, error='Completa todos los campos con números' )

    estado, datos_respuesta = api.pedir('POST', f'/api/salas', datos_back)

    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 201:
            error = api.mensaje_error(datos_respuesta)
            return render_template('admin_editar_sala.html', datos=datos,id_sala=None, error=error)

    api.flash('La nueva sala se creo correctamente', 'success')
    return redirect(url_for('locales.admin_locales'))



@salas_bp.route('/admin/salas/<int:id_sala>/editar', methods = ['GET', 'POST'])
@api.admin_front_requerido
def editar_sala(id_sala):
    datos = {}
    error = None
    if request.method == 'GET':
        filtro_estado = request.form.get('estado', 'todas')
        estado, datos_respuesta = api.pedir('GET', f'/api/salas/{id_sala}')

        estado_respuesta = api.verificar_estado(estado)
        if estado_respuesta:
            return estado_respuesta
        
        if estado != 200:
            error = api.mensaje_error(datos_respuesta)
        else:
            datos = datos_respuesta['sala']

        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    if 'nuevo_estado' in request.form:
        nuevo_estado = request.form.get('nuevo_estado')

        if nuevo_estado != 'activa':
            api.flash('Estado de sala invalido', 'error')
            return redirect(url_for('admin.admin_locales', estado=filtro_estado))

        datos_back = {'estado':nuevo_estado}    

        estado, datos_respuesta = api.pedir('PATCH', '/api/salas/{id_sala}', datos_back)

        estado_respuesta = api.verificar_estado(estado)
        if estado_respuesta:
            return estado_respuesta

        if estado != 200:
            api.flash(api.mensaje_error(datos_respuesta), 'error')
            return redirect(url_for('locales.admin_locales', estado=filtro_estado))

        api.flash('La sala se activó correctamente', 'success')
        return redirect(url_for('locales.admin_locales', estado=filtro_estado))
    datos = leer_formulario(CAMPOS_EDITAR_SALA)
    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_ENTEROS_SALA)
    
    except ValueError:
        error = 'El numero de sala y la capacidad tienen que ser numeros'
        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    estado, datos_respuesta = api.pedir('PATCH', f'/api/salas/{id_sala}', datos_back)

    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta
                
    if estado != 200:
        error = api.mensaje_error(datos_respuesta)
        return render_template('admin_editar_sala.html', datos=datos, id_sala=id_sala, error=error)
                
    api.flash('la sala se actualizó correctamente', 'success')
    return redirect(url_for('locales.admin_locales', estado=filtro_estado))

@salas_bp.route('/admin/salas/<int:id_sala>/dar_baja', methods = ['POST'])
@api.admin_front_requerido
def desactivar_sala(id_sala):
    filtro_estado = request.form.get('estado', 'todas')
    
    estado, datos_respuesta = api.pedir('DELETE', f'/api/salas/{id_sala}')

    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 200:
        api.flash(api.mensaje_error(datos_respuesta), 'error')
        return redirect(url_for('locales.admin_locales', estado=filtro_estado))
    
    api.flash('La sala se dio de baja correctamente', 'success')
    return redirect(url_for('locales.admin_locales', estado=filtro_estado))