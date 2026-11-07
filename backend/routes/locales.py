import logging
from flask import Blueprint, jsonify, request
import mysql.connector
import utils as ut
import constants as const
from services import salas as salas_services
from services import locales as locales_services

locales_bp = Blueprint('locales', __name__, url_prefix='/api')

@locales_bp.route('/locales', methods = ['GET'])
def obtener_locales():
    try:
        locales = locales_services.listar_locales()
        return jsonify({'locales':locales}), 200
    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error_db()), 500

@locales_bp.route('/locales/<id_local>/salas', methods = ['GET'])
def obtener_salas_activas(id_local):
    try:
        salas = salas_services.listar_salas_activas(id_local)
        return jsonify({'salas':salas}), 200
    
    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']
        if codigo == const.ERROR_CODE_LOCAL_NOT_FOUND:
            return jsonify(respuesta), 404

        return jsonify(respuesta), 400
    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error_db()), 500
