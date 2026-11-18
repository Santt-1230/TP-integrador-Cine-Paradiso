from flask import Blueprint, jsonify, request, session
import mysql.connector

import constants as const
import utils as ut
from services import funciones as funciones_service


funciones_bp = Blueprint("funciones", __name__, url_prefix="/api")


def error_api(codigo, mensaje, descripcion, estado):
    return jsonify(ut.construir_error_api(codigo, mensaje, descripcion)), estado


@funciones_bp.errorhandler(ValueError)
def datos_invalidos(error):
    return error_api("DATOS_INVALIDOS", "Datos inválidos", str(error), 400)


@funciones_bp.errorhandler(mysql.connector.Error)
def error_de_base_de_datos(error):
    return error_api(
        const.ERROR_CODE_DATABASE_ERROR,
        "Error de base de datos",
        "No se pudo completar la consulta",
        500,
    )


def administrador_requerido():
    if "id_usuario" not in session:
        return error_api("NO_AUTENTICADO", "No autenticado", "Inicia sesión para continuar", 401)
    if session.get("rol") != "administrador":
        return error_api("SIN_PERMISO", "Acceso denegado", "Se requiere el rol administrador", 403)
    return None


def cliente_requerido():
    if "id_usuario" not in session:
        return error_api("NO_AUTENTICADO", "No autenticado", "Inicia sesión para continuar", 401)
    if session.get("rol") != "cliente":
        return error_api("SIN_PERMISO", "Acceso denegado", "Se requiere el rol cliente", 403)
    return None


@funciones_bp.route("/funciones", methods=["GET"])
def listar_funciones():
    incluir_canceladas = request.args.get("incluir_canceladas") == "true"
    if incluir_canceladas:
        error = administrador_requerido()
        if error:
            return error

    funciones = funciones_service.listar_funciones(request.args, incluir_canceladas)
    return jsonify({"funciones": funciones}), 200


@funciones_bp.route("/funciones/<int:id_funcion>", methods=["GET"])
def obtener_funcion(id_funcion):
    funcion = funciones_service.obtener_funcion(id_funcion)
    if funcion is None:
        return error_api("FUNCION_NO_ENCONTRADA", "Función no encontrada", "No existe ese ID de función", 404)
    return jsonify({"funcion": funcion}), 200


@funciones_bp.route("/funciones/<int:id_funcion>/butacas", methods=["GET"])
def obtener_butacas(id_funcion):
    butacas = funciones_service.obtener_butacas(id_funcion)
    if butacas is None:
        return error_api("FUNCION_NO_ENCONTRADA", "Función no encontrada", "No existe ese ID de función", 404)
    return jsonify({"id_funcion": id_funcion, "butacas": butacas}), 200


@funciones_bp.route("/funciones", methods=["POST"])
def crear_funcion():
    error = administrador_requerido()
    if error:
        return error
    id_funcion, error = funciones_service.crear_funcion(request.get_json(silent=True))
    if error:
        return error_api(error[1], error[2], error[3], error[0])
    return jsonify({"id_funcion": id_funcion, "estado": "programada"}), 201


@funciones_bp.route("/funciones/<int:id_funcion>", methods=["PATCH"])
def actualizar_funcion(id_funcion):
    error = administrador_requerido()
    if error:
        return error
    funcion, error = funciones_service.actualizar_funcion(
        id_funcion, request.get_json(silent=True)
    )
    if error:
        return error_api(error[1], error[2], error[3], error[0])
    if funcion is None:
        return error_api("FUNCION_NO_ENCONTRADA", "Función no encontrada", "No existe ese ID de función", 404)
    return jsonify({"funcion": funcion}), 200