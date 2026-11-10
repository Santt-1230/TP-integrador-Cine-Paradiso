from flask import Blueprint, redirect, render_template, url_for, flash
import api

salas_bp = Blueprint('salas', __name__)

CAMPOS_NUEVA_SALA = ['id_local', 'numero_sala', 'capacidad']
CAMPOS_EDITAR_SALA = ['numero_sala', 'estado']
CAMPOS_ENTEROS_SALA = ['numero_sala']


def redirigir_al_login():
    return redirect(url_for('usuarios.login'))

def redirigir_al_inicio():
    return redirect(url_for('peliculas_front.inicio'))

def verificar_estado(estado):
    if estado == 401:
        return redirigir_al_login()
    if estado == 403:
        return redirigir_al_inicio()
    return None

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
        flash('No tenes permisos para acceder a esta seccion.', 'error')
        return redirigir_al_inicio()

    return None

@salas_bp.route('/admin/salas/nueva', methods = ['GET', 'POST'])
def crear_sala():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta

    if api.request.method == 'GET':
        datos = {'id_local' : api.request.args.get('id_local', '')}
        return render_template('admin_editar_sala.html', datos=datos, id_sala=None, error=None)

    datos = leer_formulario(CAMPOS_NUEVA_SALA)

    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_NUEVA_SALA)
    except ValueError:
        return render_template('admin_editar_sala.html', datos=datos,id_sala=None, error='Completa todos los campos con números' )

    estado, datos_respuesta = api.pedir('POST', f'/api/salas', datos_back)

    estado_respuesta = verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 201:
            error = api.mensaje_error(datos_respuesta)
            return render_template('admin_editar_sala.html', datos=datos,id_sala=None, error=error)

    flash('La nueva sala se creo correctamente', 'success')
    return redirect(url_for('locales.admin_locales'))



@salas_bp.route('/admin/salas/<int:id_sala>/editar', methods = ['GET', 'POST'])
def editar_sala(id_sala):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    
    datos = {}
    error = None
    if api.request.method == 'GET':
        estado, datos_respuesta = api.pedir('GET', f'/api/salas/{id_sala}')

        estado_respuesta = verificar_estado(estado)
        if estado_respuesta:
            return estado_respuesta
        
        if estado != 200:
            error = api.mensaje_error(datos_respuesta)
        else:
            datos = datos_respuesta['sala']

        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    datos = leer_formulario(CAMPOS_EDITAR_SALA)
    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_ENTEROS_SALA)
    
    except ValueError:
        error = 'El numero de sala tiene que ser un numero'
        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    estado, datos_respuesta = api.pedir('PATCH', f'/api/salas/{id_sala}', datos_back)

    estado_respuesta = verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta
                
    if estado != 200:
        error = api.mensaje_error(datos_respuesta)
        return render_template('admin_editar_sala.html', datos=datos, id_sala=id_sala, error=error)
                
    flash('la sala se actualizó correctamente', 'success')
    return redirect(url_for('locales.admin_locales'))

@salas_bp.route('/admin/salas/<int:id_sala>/dar_baja', methods = ['POST'])
def desactivar_sala(id_sala):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    
    estado, datos_respuesta = api.pedir('DELETE', f'/api/salas/{id_sala}')

    estado_respuesta = verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), 'error')
        return redirect(url_for('locales.admin_locales'))
    
    flash('La sala se dio de baja correctamente', 'success')
    return redirect(url_for('locales.admin_locales'))