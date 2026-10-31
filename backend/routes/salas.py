import logging
from flask import Blueprint, jsonify, request
import mysql.connector
import utils as ut
import constants as const
from services import salas as salas_services

logger = logging.getLogger(__name__)
salas_bp = Blueprint('salas', __name__, url_prefix='/api')

@salas_bp.route('/salas' , methods= ['GET'])
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
        id_sala = salas_services.crear_sala(datos)
        return jsonify({'id_sala' : id_sala}), 201

    except ValueError as error:
        return jsonify(error.args[0]), 400
    
    except (RuntimeError, mysql.connector.Error):
        jsonify(ut.construir_error_db()), 500


    
    




  