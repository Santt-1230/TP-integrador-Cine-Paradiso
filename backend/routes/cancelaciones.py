from flask import Blueprint, jsonify, request
from services.cancelaciones_service import procesar_cancelacion_cliente
from validators.cancelaciones_validator import validar_peticion_cancelacion

cancelaciones_bp = Blueprint("cancelaciones", __name__)


@cancelaciones_bp.route("/api/compras/<int:id_compra>", methods=["PATCH"])
def cancelar_compra_route(id_compra: int):
    datos = request.get_json(silent=True)

    es_valido, mensaje_error = validar_peticion_cancelacion(datos)
    if not es_valido:
        return jsonify({"exito": False, "mensaje": mensaje_error}), 400

    respuesta, status_code = procesar_cancelacion_cliente(id_compra)
    return jsonify(respuesta), status_code