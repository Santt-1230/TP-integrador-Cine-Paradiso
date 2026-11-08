from flask import Blueprint, redirect, session, render_template, request, url_for, flash
import api

salas_bp = Blueprint('salas', __name__)

CAMPOS_NUEVA_SALA = ['id_local', 'numero_sala', 'capacidad']
CAMPOS_EDITAR_SALA = ['numero_sala', 'estado']
CAMPOS_ENTEROS_SALA = ['numero_sala']
def sesion_invalida(error_api):
    return error_api.estado in (401, 403)

def redirigir_al_login():
    return redirect(url_for('usuarios.login'))

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
@salas_bp.route('/salas/<int:id_sala>/butacas', methods = ['GET', 'POST'])
def elegir_butacas(id_sala):
    butacas = []
    error = None

    try:
        butacas = api.get(f'/api/salas/{id_sala}/butacas')['butacas']

    except api.ApiError as error_api:
        error = error_api.mensaje

    if request.method == 'POST' and error is None:
        ids_validos = []
        for butaca in butacas:
            ids_validos.append(str(butaca['id_butaca']))
        elegidas = []
        for id_butaca in request.form.getlist('butacas'):
            if id_butaca in ids_validos:
                elegidas.append(id_butaca)

        if not elegidas:
            error = "Elegi al menos una butaca"

        else:
            butacas_elegidas = []
            for id_butaca in elegidas:
                butacas_elegidas.append(int(id_butaca))

            session['id_sala'] = id_sala
            session['butacas_elegidas'] = butacas_elegidas
            return redirect('/')
    return render_template('butacas.html', butacas = butacas,id_sala = id_sala, error = error)

@salas_bp.route('/admin/salas/<int:id_sala>/editar', methods = ['GET', 'POST'])
def editar_sala(id_sala):
    datos = {}
    error = None
    if request.method == 'GET':
        try:
            datos = api.pedir('GET', f'/api/salas/{id_sala}')['sala']

        except api.ApiError as error_api:
            if sesion_invalida(error_api):
                redirigir_al_login()
            error_api.mensaje

        return render_template('admin_editar_sala.html', datos = datos, id_sala = id_sala, error = error)

    datos = leer_formulario(CAMPOS_EDITAR_SALA)
    try:
        datos_back = convertir_a_enteros(datos, CAMPOS_ENTEROS_SALA)
        api.pedir('PATCH', f'/api/salas/{id_sala}', datos_back)
        flash('la sala se actualizó correctamente')
        return redirect(url_for('locales.admin_locales'))
    
    except ValueError:
        error = 'El numero de sala tiene que ser un numero'

    except api.ApiError as error_api:
        if sesion_invalida(error_api):
            redirigir_al_login()
        error = error_api.mensaje

    return render_template('admin_editar_sala.html', datos=datos, id_sala=id_sala, error=error), 400