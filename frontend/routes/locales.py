import os
import requests
from flask import Blueprint, redirect,session, render_template, request, url_for
from api import BACKEND_URL

locales_bp = Blueprint('locales', __name__)

@locales_bp.route('/locales', methods = ['GET'])
def mostrar_locales():
    try:
        respuesta = requests.get(f"{BACKEND_URL}/api/locales", timeout = 5)
        respuesta.raise_for_status()
        locales = respuesta.json()
        error = None
    except requests.RequestException:
        locales = []
        error = 'No se pudieron cargar los locales, asegurese que el backend este iniciado'

    return render_template("locales.html", locales = locales, error = error)

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