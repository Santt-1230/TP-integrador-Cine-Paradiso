from flask import Blueprint, jsonify, request
from mysql.connector import IntegrityError  

from repositories.admin import (
    actualizar_usuario,
    obtener_usuario_por_id,
    obtener_usuarios,
    obtener_cantidad_peliculas_activas,
    obtener_cantidad_funciones_programadas
)
from validators.admin import( 
    validar_actualizacion_usuario
)

from utils import admin_requerido
from constants import ROLES_VALIDOS


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/usuarios", methods=["GET"])
@admin_requerido
def get_usuarios():
    return jsonify(obtener_usuarios()), 200


@admin_bp.route("/usuarios/<int:id>/editar", methods=["GET"])
@admin_requerido
def get_usuario(id):
    usuario = obtener_usuario_por_id(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuario), 200

@admin_bp.route("/usuarios/<int:id>/editar", methods=["PATCH"])
@admin_requerido
def update_usuario(id):
    data = request.get_json(silent=True)
    datos, error = validar_actualizacion_usuario(data)

    if error:
        return jsonify({"error": error}), 400

    if not obtener_usuario_por_id(id):
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        actualizar_usuario(
            id,
            datos["nombre"],
            datos["email"],
            datos["rol"]
        )
    except IntegrityError:
        return jsonify({"error": "Ese correo ya está en uso"}), 409

    return jsonify({"message": "Usuario actualizado correctamente"}), 200


@admin_bp.route("/peliculas/activa", methods=["GET"])
@admin_requerido
def get_peliculas_activas():

    cantidad = obtener_cantidad_peliculas_activas()

    return jsonify({"total": cantidad}), 200



@admin_bp.route("/funciones/programadas", methods=["GET"])
@admin_requerido
def get_funciones_programadas():

    cantidad = obtener_cantidad_funciones_programadas()

    return jsonify({"total": cantidad}), 200