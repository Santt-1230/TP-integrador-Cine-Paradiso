from flask import Blueprint, jsonify, request 

from backend.services import estadisticas as estadisticas_service
from backend.validators.admin import requiere_admin

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.route("/ocupacion", methods=["GET"])
@requiere_admin
def get_estadisticas_ocupacion():
    resultado = estadisticas_service.obtener_estadisticas_ocupacion()
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_totales", methods=["GET"])
@requiere_admin
def get_estadisticas_ventas():
    periodo = request.args.get("periodo", "mensual")
    resultado = estadisticas_service.obtener_estadisticas_ventas(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_entradas", methods=["GET"])
@requiere_admin
def get_estadisticas_ventas_entradas():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_ventas_entradas(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/venta_servicios", methods=["GET"])
@requiere_admin
def get_estadisticas_venta_servicios():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_ventas_servicios(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_por_genero", methods=["GET"])
@requiere_admin
def get_estadisticas_ventas_por_genero():
    resultado = estadisticas_service.obtener_ventas_por_genero()
    return jsonify(resultado), 200


@estadisticas_bp.route("/cancelaciones", methods=["GET"])
@requiere_admin
def get_estadisticas_cancelaciones():
    periodo = request.args.get("periodo")
    resultado = estadisticas_service.obtener_estadisticas_cancelaciones(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/franjas_horarias", methods=["GET"])
@requiere_admin
def get_estadisticas_franjas_horarias():
    resultado = estadisticas_service.obtener_estadisticas_franjas_horarias()
    return jsonify(resultado), 200