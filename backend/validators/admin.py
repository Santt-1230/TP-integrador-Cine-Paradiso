from functools import wraps
from flask import session, jsonify


def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        usuario = session.get("usuario")

        if not usuario:
            return jsonify({"error": "No estás autenticado"}), 401

        if usuario.get("rol") != "admin":
            return jsonify({"error": "No tenés permisos de administrador"}), 403

        return func(*args, **kwargs)

    return wrapper