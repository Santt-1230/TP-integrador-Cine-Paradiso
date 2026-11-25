from flask import Blueprint, jsonify, request

from repositories.estadisticas import (
    obtener_ocupacion_por_funcion,

)

from services.estadisticas import obtener_dashboard_estadisticas
from utils import admin_requerido


estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


def ejecutar_consulta_periodo(funcion, *args):

    periodo = request.args.get("periodo", "30")

    try:
        resultado = funcion(*args, periodo=periodo)
        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400


# DASHBOARD COMPLETO

@estadisticas_bp.route("/dashboard", methods=["GET"])
@admin_requerido
def get_estadisticas_dashboard():
    return ejecutar_consulta_periodo(
        obtener_dashboard_estadisticas
    )

# OCUPACIÓN Promedio

@estadisticas_bp.route("/ocupacion", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion():
    return ejecutar_consulta_periodo(
        obtener_ocupacion_por_funcion   
    )
