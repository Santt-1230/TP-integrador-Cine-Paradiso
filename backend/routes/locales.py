from flask import Blueprint, jsonify, request
import mysql.connector
from utils import (admin_requerido, construir_error_db)
from constants import ERROR_CODE_LOCAL_NOT_FOUND, ERROR_CODE_LOCAL_INACTIVE
from services import salas as salas_services
from services import locales as locales_services
from utils import admin_requerido
locales_bp = Blueprint('locales', __name__, url_prefix='/api')

@locales_bp.route('/locales', methods = ['GET'])
def obtener_locales():
    try:
        locales = locales_services.listar_locales()
        return jsonify({'locales':locales}), 200
    except (RuntimeError, mysql.connector.Error):
        return jsonify(construir_error_db()), 500

@locales_bp.route('/locales/<id_local>', methods = ['GET'])
def obtener_local(id_local):
    try:
        local = locales_services.obtener_local(id_local)
        return jsonify({'local': local}), 200

    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']

        if codigo == ERROR_CODE_LOCAL_NOT_FOUND:
            return jsonify(respuesta), 404

        if codigo == ERROR_CODE_LOCAL_INACTIVE:
            return jsonify(respuesta), 409

        return jsonify(respuesta), 400

    except (RuntimeError, mysql.connector.Error):
        return jsonify(construir_error_db()), 500


@locales_bp.route('/locales/<id_local>/salas', methods = ['GET'])
@admin_requerido
def obtener_salas_activas(id_local):
    try:
        salas = salas_services.listar_salas(id_local, 'activa')
        return jsonify({'salas':salas}), 200
    
    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']
        if codigo == ERROR_CODE_LOCAL_NOT_FOUND:
            return jsonify(respuesta), 404

        return jsonify(respuesta), 400
    except (RuntimeError, mysql.connector.Error):
        return jsonify(construir_error_db()), 500

@locales_bp.route('/locales/resumen-salas', methods=['GET'])
@admin_requerido
def obtener_resumen_salas():
    id_local = request.args.get('local')
    estado = request.args.get('estado')
    try:
        return jsonify(locales_services.resumen_salas(id_local, estado)), 200
    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']
        if codigo == ERROR_CODE_LOCAL_NOT_FOUND:
            return jsonify(respuesta), 404
        return jsonify(respuesta), 400
    except (RuntimeError, mysql.connector.Error):
        return jsonify(construir_error_db()), 500