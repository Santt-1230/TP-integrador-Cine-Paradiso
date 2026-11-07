from flask import Blueprint, redirect, session, render_template, request
import api

salas_bp = Blueprint('salas', __name__)

CAMPOS_NUEVA_SALA = ['id_local', 'numero_sala', 'capacidad']
CAMPOS_EDITAR_SALA = ['id_local', 'numero_sala']

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