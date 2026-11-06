from flask import Blueprint, jsonify, request 
from repositories.estadisticas import (
    obtener_ventas_totales, obtener_ventas_entradas, 
    obtener_ventas_productos, obtener_ventas_por_genero, 
    obtener_cancelaciones, obtener_entradas_vendidas_por_franja,
    obtener_ocupacion_por_funcion, obtener_ocupacion_por_pelicula)
from utils import admin_requerido

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.route("/ocupacion/<int:id_funcion>", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion(id_funcion):
    resultado = obtener_ocupacion_por_funcion(id_funcion)
    return jsonify(resultado), 200

@estadisticas_bp.route("/ocupacion/pelicula/<int:id_pelicula>", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion_pelicula(id_pelicula):
    resultado = obtener_ocupacion_por_pelicula(id_pelicula)
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_totales", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas():
    periodo = request.args.get("periodo", "mensual")
    resultado = obtener_ventas_totales(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_entradas", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas_entradas():
    periodo = request.args.get("periodo")
    resultado = obtener_ventas_entradas(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/venta_servicios", methods=["GET"])
@admin_requerido
def get_estadisticas_venta_servicios():
    periodo = request.args.get("periodo")
    resultado = obtener_ventas_productos(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/ventas_por_genero", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas_por_genero():
    resultado = obtener_ventas_por_genero()
    return jsonify(resultado), 200


@estadisticas_bp.route("/cancelaciones", methods=["GET"])
@admin_requerido
def get_estadisticas_cancelaciones():
    periodo = request.args.get("periodo")
    resultado = obtener_cancelaciones(periodo)
    return jsonify(resultado), 200


@estadisticas_bp.route("/franjas_horarias", methods=["GET"])
@admin_requerido
def get_estadisticas_franjas_horarias():
    resultado = obtener_entradas_vendidas_por_franja()
    return jsonify(resultado), 200