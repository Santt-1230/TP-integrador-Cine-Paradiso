from flask import Blueprint, jsonify, request 
from flask_jwt_extended import jwt_required

from backend.services import estadisticas as estadisticas_service
from backend.validators.admin import requiere_admin

estadisticas_bp = Blueprint("estadisticas", __name__)


@estadisticas_bp.route("/estadisticas/ocupacion", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_ocupacion():
    resultado = estadisticas_service.obtener_estadisticas_ocupacion()
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/ventas_totales", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_ventas():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_estadisticas_ventas(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/ventas_entradas", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_ventas_entradas():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_ventas_entradas(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/venta_servicios", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_venta_servicios():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_ventas_servicios(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/ventas_por_genero", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_ventas_por_genero():
    resultado = estadisticas_service.obtener_ventas_por_genero()
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/cancelaciones", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_cancelaciones():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_estadisticas_cancelaciones(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/estadisticas/franjas_horarias", methods=["GET"])
@jwt_required()
@requiere_admin
def get_estadisticas_franjas_horarias():
    resultado = estadisticas_service.obtener_estadisticas_franjas_horarias()
    return jsonify(resultado), 200