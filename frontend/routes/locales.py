from flask import Blueprint, redirect,session, render_template, request, url_for

locales_bp = Blueprint('locales', __name__)
LOCALES_PRUEBA = [{'id_local':1, 'nombre': 'Cine Centro', 'salas': [{
            'id_sala':1, 'numero_sala':1, 'capacidad':120, 'estado' : 'activa'},
            {
            'id_sala':2, 'numero_sala':2, 'capacidad':133, 'estado' : 'activa'}
        ]},
        {'id_local':2, 'nombre': 'Cine Norte', 'salas': [{
        'id_sala':3, 'numero_sala':1, 'capacidad':39, 'estado' : 'activa'},
        {
        'id_sala':4, 'numero_sala':2, 'capacidad':200, 'estado' : 'activa'}
        ]}, {'id_local':3, 'nombre': 'Cine Sur', 'salas': [{
                'id_sala':5, 'numero_sala':1, 'capacidad':100, 'estado' : 'activa'},
                {
                'id_sala':6, 'numero_sala':2, 'capacidad':138, 'estado' : 'activa'}
            ]}
        ]

@locales_bp.route('/prueba-locales', methods = ['GET'])
def probar_locales():
    return render_template("inicio.html", locales = LOCALES_PRUEBA)

@locales_bp.route('/elegir-cine/<int:id_local>', methods = ['GET'])
def elegir_cine(id_local):
    local = next(
        (
            item for item in LOCALES_PRUEBA
            if item['id_local'] == id_local
        ),
        None
    )
    if local is None:
        return "Local no encontrado", 404

    session['id_local'] = local['id_local']
    session['cine_nombre'] = local['nombre']
    return redirect(url_for('locales.probar_locales'))

@locales_bp.route('/prueba-admin-locales', methods=['GET'])
def probar_admin_locales():
    salas_configuradas = 0
    for local in LOCALES_PRUEBA:
        local['total_butacas'] = sum(
            sala['capacidad'] for sala in local['salas']
        )
        salas_configuradas += len(local['salas'])
    return render_template("admin_locales.html", locales=LOCALES_PRUEBA, salas_configuradas=salas_configuradas)

@locales_bp.route('/prueba-nueva-sala', methods = ['GET'])
def probar_nueva_sala():
    id_local = request.args.get('id_local', type=int)
    local = next(
            (
                item for item in LOCALES_PRUEBA
                if item['id_local'] == id_local
            ),
            None
    )
    if local is None:
        return "Local no encontrado", 404
    
    return render_template("admin_nueva_sala.html", local=local,locales=LOCALES_PRUEBA)

@locales_bp.route('/prueba-editar-sala', methods=['GET'])
def probar_editar_sala():
        id_sala=request.args.get('id_sala', type=int)
        id_local = request.args.get('id_local', type=int)
        local = next(
            (
                item for item in LOCALES_PRUEBA
                if item['id_local'] == id_local
            ),
            None
        )
        if local is None:
            return "Local no encontrado", 404
        
        sala = next(
            (
                item for item in local['salas']
                if item['id_sala'] == id_sala
            ),
            None
        )
        if sala is None:
            return "Local no encontrado", 404
        
        return render_template("admin_editar_sala.html", sala=sala,local=local, locales=LOCALES_PRUEBA)