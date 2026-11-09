from flask import Blueprint, jsonify, request

from repositories.estadisticas import (
    obtener_ventas_totales,
    obtener_ventas_entradas,
    obtener_ventas_productos,
    obtener_ventas_por_genero,
    obtener_cancelaciones,
    obtener_entradas_vendidas_por_franja,
    obtener_ocupacion_por_funcion,
    obtener_ocupacion_por_pelicula
)

from utils import admin_requerido


estadisticas_bp = Blueprint(
    "estadisticas",
    __name__,
    url_prefix="/api/estadisticas"
)



def ejecutar_consulta_periodo(funcion, *args):

    periodo = request.args.get("periodo", "30")

    try:
        resultado = funcion(*args, periodo=periodo)
        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400



@estadisticas_bp.route("/ventas_totales", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas():
    return ejecutar_consulta_periodo(obtener_ventas_totales)


@estadisticas_bp.route("/ventas_entradas", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas_entradas():
    return ejecutar_consulta_periodo(obtener_ventas_entradas)


@estadisticas_bp.route("/venta_servicios", methods=["GET"])
@admin_requerido
def get_estadisticas_venta_servicios():
    return ejecutar_consulta_periodo(obtener_ventas_productos)


@estadisticas_bp.route("/ventas_por_genero", methods=["GET"])
@admin_requerido
def get_estadisticas_ventas_por_genero():
    return ejecutar_consulta_periodo(obtener_ventas_por_genero)




@estadisticas_bp.route("/cancelaciones", methods=["GET"])
@admin_requerido
def get_estadisticas_cancelaciones():
    return ejecutar_consulta_periodo(obtener_cancelaciones)



@estadisticas_bp.route("/franjas_horarias", methods=["GET"])
@admin_requerido
def get_estadisticas_franjas_horarias():
    return ejecutar_consulta_periodo(
        obtener_entradas_vendidas_por_franja
    )



@estadisticas_bp.route("/ocupacion", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion():
    return ejecutar_consulta_periodo(
        obtener_ocupacion_por_funcion
    )


@estadisticas_bp.route("/ocupacion/<int:id_funcion>", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion_funcion(id_funcion):
    return ejecutar_consulta_periodo(
        obtener_ocupacion_por_funcion,
        id_funcion
    )


@estadisticas_bp.route("/ocupacion/peliculas", methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion_peliculas():
    return ejecutar_consulta_periodo(
        obtener_ocupacion_por_pelicula
    )


@estadisticas_bp.route("/ocupacion/pelicula/<int:id_pelicula>",methods=["GET"])
@admin_requerido
def get_estadisticas_ocupacion_pelicula(id_pelicula):
    return ejecutar_consulta_periodo(
        obtener_ocupacion_por_pelicula,
        id_pelicula
    )