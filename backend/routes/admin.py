from flask import Blueprint, jsonify, request 
from backend.repositories import admin
from backend.validators.admin import requiere_admin 

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/usuarios", methods=["GET"])
@requiere_admin
def get_usuarios():
    usuarios = admin.obtener_usuarios()
    return jsonify(usuarios), 200


@admin_bp.route("/usuarios/<int:id>/editar", methods = ["GET"])
@requiere_admin
def get_usuario(id):
    usuario = admin.obtener_usuario_por_id(id)
    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404



@admin_bp.route("/usuarios/<int:id>/editar", methods = ["PATCH"])
@requiere_admin
def update_usuario(id):
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    rol = data.get("rol")

    if not nombre or not email or not rol:
        return jsonify({"error": "Faltan datos requeridos"}), 400

    admin.actualizar_usuario(id, nombre, email, rol)
    return jsonify({"message": "Usuario actualizado correctamente"}), 200

