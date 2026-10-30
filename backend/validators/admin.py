from functools import wraps
from flask import session, jsonify


def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if session.get("id_usuario") is None:
            return jsonify({"error": "Debés iniciar sesión"}), 401

        if session.get("rol") != "admin":
            return jsonify({"error": "No tenés permisos de administrador"}), 403

        return func(*args, **kwargs)

    return wrapper


def validar_rol(rol):
    roles_permitidos = ["cliente", "admin"]

    return rol in roles_permitidos


def validar_actualizacion_usuario(nombre=None, email=None, rol=None):

    if nombre is not None:
        if not nombre.strip():
            return False

    if email is not None:
        if not email.strip():
            return False

    if rol is not None:
        if not validar_rol(rol):
            return False

    return True