from flask import Blueprint, render_template, redirect, url_for, request
import api

salas_bp = Blueprint('salas', __name__)

FILAS_INICIALES = [{'fila': 'A', 'cantidad': 10}]


def datos_sala_desde_form(request_form):
    numero_sala = request_form.get("numero_sala", "").strip()
    
    letras = request_form.getlist("fila")
    cantidades = request_form.getlist("cantidad")
    
    filas_form = [{'fila': l, 'cantidad': c} for l, c in zip(letras, cantidades)] if letras else FILAS_INICIALES

    return {
        "numero_sala": numero_sala,
        "letras": letras,
        "cantidades": cantidades,
    }, filas_form


@salas_bp.route("/admin/salas/nueva", methods=["GET", "POST"])
@api.admin_front_requerido
def crear_sala():
    id_local = request.args.get("id_local", type=int)
    filtro_estado = request.values.get("filtro_estado", "todas")
    filtro_local = request.values.get("filtro_local", type=int)

    if request.method == "GET":
        return render_template(
            "admin_editar_sala.html",
            sala=None,
            id_local=id_local,
            numero_sala="",
            filas=FILAS_INICIALES,
            filtro_estado=filtro_estado,
            filtro_local=filtro_local,
            error=None
        )

    datos, filas_form = datos_sala_desde_form(request.form)
    datos["id_local"] = id_local

    estado, datos_respuesta = api.pedir("POST", "/api/salas", datos)
    
    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 201:
        return render_template(
            "admin_editar_sala.html",
            sala=None,
            id_local=id_local,
            numero_sala=datos["numero_sala"],
            filas=filas_form,
            filtro_estado=filtro_estado,
            filtro_local=filtro_local, 
            error=api.mensaje_error(datos_respuesta)
        )

    api.flash("Sala creada correctamente.", "success")
    return redirect(url_for("locales.admin_locales", estado=filtro_estado, local=filtro_local))


@salas_bp.route('/admin/salas/<int:id_sala>/editar', methods=['GET', 'POST'])
@api.admin_front_requerido
def editar_sala(id_sala):
    filtro_estado = request.values.get('filtro_estado', 'todas')
    filtro_local = request.values.get('filtro_local', type=int)
    if request.method == 'GET':
        estado, resp = api.pedir('GET', f'/api/salas/{id_sala}')
        estado_respuesta = api.verificar_estado(estado)
        if estado_respuesta:
            return estado_respuesta
        if estado != 200:
            api.flash(api.mensaje_error(resp), 'error')
            return redirect(url_for('locales.admin_locales', 
                    estado=filtro_estado, local=filtro_local))
        
        sala = resp['sala']
        
        estado_filas, resp_filas = api.pedir('GET', f'/api/salas/{id_sala}/filas')
        estado_respuesta = api.verificar_estado(estado_filas)
        if estado_respuesta:
            return estado_respuesta
        if estado_filas != 200:
            api.flash(api.mensaje_error(resp_filas), 'error')
            return redirect(url_for('locales.admin_locales',
                estado=filtro_estado, local=filtro_local))
        filas_sala = resp_filas['filas'] or FILAS_INICIALES

        return render_template(
            'admin_editar_sala.html',
            sala=sala,
            id_local=sala.get('id_local'),
            numero_sala=sala['numero_sala'],
            filas=filas_sala,
            filtro_estado=filtro_estado,
            filtro_local = filtro_local,
            error=None
        )

    datos, filas_form = datos_sala_desde_form(request.form)
    

    estado, resp = api.pedir('PATCH', f'/api/salas/{id_sala}', datos)
    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 200:
        sala = {'id_sala': id_sala, 'numero_sala': datos['numero_sala']}
        
        return render_template('admin_editar_sala.html', sala=sala, id_local=None,
            numero_sala=datos['numero_sala'], filas=filas_form, filtro_estado=filtro_estado, 
            filtro_local=filtro_local, error=api.mensaje_error(resp)
        )

    api.flash('La sala se actualizó correctamente', 'success')
    return redirect(url_for('locales.admin_locales', 
        estado=filtro_estado, local=filtro_local))


@salas_bp.route('/admin/salas/<int:id_sala>/dar_baja', methods=['POST'])
@api.admin_front_requerido
def desactivar_sala(id_sala):
    filtro_estado = request.form.get('filtro_estado', 'todas')
    filtro_local = request.form.get('filtro_local', type=int)

    estado, datos_respuesta = api.pedir('DELETE', f'/api/salas/{id_sala}')

    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado not in (200, 204):
        api.flash(api.mensaje_error(datos_respuesta), 'error')
    else:
        api.flash('La sala se dio de baja correctamente', 'success')

    return redirect(url_for('locales.admin_locales', estado=filtro_estado, local=filtro_local))


@salas_bp.route('/admin/salas/<int:id_sala>/activar', methods=['POST'])
@api.admin_front_requerido
def activar_sala(id_sala):
    filtro_estado = request.form.get('filtro_estado', 'todas')
    filtro_local = request.form.get('filtro_local', type=int)
    
    estado, datos_respuesta = api.pedir('PATCH', f'/api/salas/{id_sala}', {'estado': 'activa'})

    estado_respuesta = api.verificar_estado(estado)
    if estado_respuesta:
        return estado_respuesta

    if estado != 200:
        api.flash(api.mensaje_error(datos_respuesta), 'error')
    else:
        api.flash('La sala se activó correctamente', 'success')

    return redirect(url_for('locales.admin_locales', estado=filtro_estado, local=filtro_local))