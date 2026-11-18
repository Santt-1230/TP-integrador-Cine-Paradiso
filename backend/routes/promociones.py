from flask import Blueprint, jsonify, request
from services.promociones import (
    listar_promociones,
    listar_promocion_por_id,
    crear_promocion,
    actualizar_promocion,
    dar_de_baja_promocion,
)
from validators.promociones import validar_creacion, validar_modificacion
from utils import construir_error_api

promociones_bp = Blueprint('promociones', __name__, url_prefix='/api')


def error_no_encontrado(id_promocion):
    error = construir_error_api(
            code = 'promocion.not_found',
            message = 'Promocion no encontrada',
            description = f'No existe una promocion con el id {id_promocion}'
        )
    return jsonify(error), 404


def error_datos_invalidos(mensaje):
    error = construir_error_api('promocion.invalid_data', 'Datos invalidos', mensaje)
    return jsonify(error), 400


@promociones_bp.route('/promociones', methods=['GET'])
def obtener_promociones_route():
    incluir_inactivas = request.args.get('incluir_inactivas') == 'true'
    promociones = listar_promociones(incluir_inactivas)
    return jsonify(promociones), 200


@promociones_bp.route('/promociones/<int:id_promocion>', methods=['GET'])
def obtener_promocion_por_id_route(id_promocion):
    promocion = listar_promocion_por_id(id_promocion)
    if promocion is None:
        return error_no_encontrado(id_promocion)
    return jsonify(promocion), 200


@promociones_bp.route('/promociones', methods=['POST'])
def crear_promocion_route():
    datos = request.get_json(silent=True)
    mensaje = validar_creacion(datos)
    if mensaje:
        return error_datos_invalidos(mensaje)
    promocion = crear_promocion(datos)
    return jsonify(promocion), 201


@promociones_bp.route('/promociones/<int:id_promocion>', methods=['PATCH'])
def modificar_promocion_route(id_promocion):
    datos = request.get_json(silent=True)
    mensaje = validar_modificacion(datos)
    if mensaje:
        return error_datos_invalidos(mensaje)
    promocion = actualizar_promocion(id_promocion, datos)
    if promocion is None:
        return error_no_encontrado(id_promocion)
    return jsonify(promocion), 200


@promociones_bp.route('/promociones/<int:id_promocion>', methods=['DELETE'])
def dar_de_baja_promocion_route(id_promocion):
    se_dio_de_baja = dar_de_baja_promocion(id_promocion)
    if not se_dio_de_baja:
        return error_no_encontrado(id_promocion)
    return jsonify({"mensaje": "Promocion dada de baja"}), 200
