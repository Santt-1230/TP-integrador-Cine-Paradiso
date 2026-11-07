import logging
from flask import Blueprint, jsonify, request
import mysql.connector
import utils as ut
import constants as const
from services import salas as salas_services


logger = logging.getLogger(__name__)
salas_bp = Blueprint('salas', __name__, url_prefix='/api')

@salas_bp.route('/salas' , methods= ['GET'])
@ut.admin_requerido
def obtener_salas():
    id_local = request.args.get('id_local')
    try: 
        salas = salas_services.listar_salas(id_local)
        return jsonify({'salas':salas}), 200

    except ValueError as error:
        return jsonify(error.args[0]), 400
    
    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error_db()), 500

@salas_bp.route('/salas<id_sala>', methods=['GET'])
def obtener_sala_id(id_sala):
    try:
        sala = salas_services.listar_sala_id(id_sala)

        if sala is None:
            error = ut.construir_error_api(
                code=const.ERROR_CODE_SALA_NOT_FOUND,
                message='Sala no encontrada',
                description=f"No existe una sala registrada con el ID '{id_sala}'."
            )
            return jsonify(error), 404
        
        return jsonify({sala:'sala'}), 200
    
    except ValueError as error:
        return jsonify(error.args[0]), 400
    
    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error_db()), 500

@salas_bp.route('/salas', methods = ['POST'])
@ut.admin_requerido
def crear_sala(datos):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        respuesta = ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Datos invalidos',
            description='El formato debe ser un JSON con id_local, numero_sala, capacidad'
        )
        return jsonify(respuesta), 400
    try:
        sala = salas_services.crear_sala(datos)
        return jsonify({'sala' : sala}), 201

    except ValueError as error:
        return jsonify(error.args[0]), 400
    
    except (RuntimeError, mysql.connector.Error):
        jsonify(ut.construir_error_db()), 500

@salas_bp.route('/salas/<id_sala>/butacas', methods= ['GET'])
def obtener_butacas_sala(id_sala):
    try:
        butacas = salas_services.obtener_butacas_sala(id_sala)
        if butacas is None:
            respuesta = ut.construir_error_api(
                code=const.ERROR_CODE_SALA_NOT_FOUND,
                message='Sala no encontrada',
                description=f"No existe una sala con el id '{id_sala}'."
            )
            return jsonify(respuesta), 404
        
        return jsonify({'butacas':butacas}), 200

    except ValueError as error:
        return jsonify(error.args[0]), 400

    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error_db()), 500


@salas_bp.route('/salas<id_sala>', methods = ['PATCH'])
@ut.admin_requerido
def actualizar_sala(id_sala):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        respuesta = ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Datos invalidos',
            description='Envia un JSON con los campos que desees modificar'
        )
        return jsonify(respuesta), 400
    try:
        sala = salas_services.actualizar_sala(id_sala)
        return jsonify({'sala':sala}), 200

    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']

        if codigo == const.ERROR_CODE_SALA_NOT_FOUND:
            return jsonify(respuesta), 404

        if codigo == const.ERROR_CODE_SALA_CONFLICT:
            return jsonify(respuesta), 409

        return jsonify(respuesta), 400

    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error.db()), 500
    
    
@salas_bp.route('/salas/<id_sala>', methods = ['DELETE'])
@ut.admin_requerido
def desactivar_sala(id_sala):
    try:
        sala = salas_services.desactivar_sala(id_sala)
        return jsonify(sala), 200

    except ValueError as error:
        respuesta = error.args[0]
        codigo = respuesta['errors'][0]['code']

        if codigo == const.ERROR_CODE_SALA_NOT_FOUND:
            return jsonify(respuesta), 404
        
        return jsonify(respuesta), 400
        
    except (RuntimeError, mysql.connector.Error):
        return jsonify(ut.construir_error.db()), 500





  