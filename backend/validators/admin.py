from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt



def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        claims = get_jwt()

        if claims.get("rol") != "admin":
            return jsonify({
                "error": "No tenés permisos de administrador"
            }), 403

        return func(*args, **kwargs)

    return wrapper


def validar_rol(rol):
    roles_permitidos = ["cliente", "admin"]

    return rol in roles_permitidos


def validar_actualizacion_usuario(nombre, email, rol):
    if not nombre or not nombre.strip():
        return False

    if not email or not email.strip():
        return False

    if not validar_rol(rol):
        return False

    return True