from flask import Blueprint, jsonify, request
from mysql.connector import IntegrityError  

from repositories.admin import (
    actualizar_usuario,
    obtener_usuario_por_id,
    obtener_usuarios,
    obtener_cantidad_peliculas_activas
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

    if not isinstance(data, dict):
        data = {}

    nombre = str(data.get("nombre") or "").strip()
    email = str(data.get("email") or "").strip()
    rol = str(data.get("rol") or "").strip()

    if not nombre or not email or not rol:
        return jsonify({"error": "Faltan datos requeridos"}), 400

    if rol not in ROLES_VALIDOS:
        return jsonify({"error": "El rol no es válido"}), 400

    if not obtener_usuario_por_id(id):
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        actualizar_usuario(id, nombre, email, rol)
    except IntegrityError:
        return jsonify({"error": "Ese correo ya está en uso"}), 409

    return jsonify({"message": "Usuario actualizado correctamente"}), 200

admin_bp.route("/peliculas/activa", methods=["GET"])
@admin_requerido
def get_peliculas_activas():
    cantidad = obtener_cantidad_peliculas_activas()
    return jsonify({"cantidad": cantidad}), 200