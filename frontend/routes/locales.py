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
        ]}, {'id_local':3, 'nombre': 'Cine Centro', 'salas': [{
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
    local_elegido = next(
        (
            local for local in LOCALES_PRUEBA
            if local['id_local'] == id_local
        ),
        None
    )
    if local_elegido:
        session['id_local'] = local_elegido['id_local']
        session['cine_nombre'] = local_elegido['nombre']
    return redirect(url_for('locales.probar_locales'))

@locales_bp.route('/prueba-admin-locales', methods=['GET'])
def probar_admin_locales():
    return render_template("admin_locales.html", locales=LOCALES_PRUEBA)