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
        respuesta = ut.construir_error_api(
            code=const.ERROR_CODE_DATABASE_ERROR,
            message='No se pudieron listar las salas',
            description='Ocurrio un problema al consultar la base de datos'
        )
        return jsonify(respuesta), 500

    
    




  