from flask import Blueprint, jsonify, request
from services.servicios import (
    listar_servicios,
    listar_servicio_por_id,
    crear_servicio,
    actualizar_servicio,
    dar_de_baja_servicio
)
from validators.servicios import validar_creacion, validar_modificacion
from utils import construir_error_api

servicios_bp = Blueprint('servicios', __name__, url_prefix="/api")


def error_no_encontrado(id_producto):
    error = construir_error_api(
            code = 'servicio.not_found',
            message = 'Servicio no encontrado',
            description = f'No existe un servicio con el id {id_producto}'
        )
    return jsonify(error), 404


@servicios_bp.route('/servicios', methods=['GET'])
def obtener_servicios_route():
    incluir_inactivos = request.args.get('incluir_inactivos') == 'true'
    servicios = listar_servicios(incluir_inactivos)
    return jsonify(servicios), 200


@servicios_bp.route('/servicios/<id_producto>', methods=['GET'])
def obtener_servicio_por_id_route(id_producto):
    servicio = listar_servicio_por_id(id_producto)
    if servicio is None:
        return error_no_encontrado(id_producto)
    return jsonify(servicio), 200


@servicios_bp.route('/servicios', methods=['POST'])
def crear_servicio_route():
    datos = request.get_json(silent=True)
    mensaje = validar_creacion(datos)
    if mensaje:
        error = construir_error_api('servicio.invalid_data', 'Datos invalidos', mensaje)
        return jsonify(error), 400
    servicio = crear_servicio(datos)
    return jsonify(datos), 201


@servicios_bp.route('/servicios/<id_producto>', methods=['PATCH'])
def modificar_servicio_route(id_producto):
    datos = request.get_json(silent=True)
    mensaje = validar_modificacion(datos)
    if mensaje:
        error = construir_error_api('servicio.invalid_data', 'Datos invalidos', mensaje)
        return jsonify(error), 400
    servicio = actualizar_servicio(id_producto, datos)
    if servicio is None:
        return error_no_encontrado(id_producto)
    return jsonify(datos), 200


@servicios_bp.route('/servicios/<id_producto>', methods=['DELETE'])
def dar_de_baja_servicio_route(id_producto):
    se_dio_de_baja = dar_de_baja_servicio(id_producto)
    if not se_dio_de_baja:
        return error_no_encontrado(id_producto)
    return jsonify({"mensaje": "Servicio dado de baja"}), 200