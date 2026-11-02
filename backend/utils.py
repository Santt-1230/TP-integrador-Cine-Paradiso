from flask import jsonify, session
from functools import wraps
import logging
import constants as const

logger = logging.getLogger(__name__)

def construir_error_api(code:str, message:str, description:str, level:str = 'error')->dict:
    return {
        'errors' :[{
            "error" : level,
            "code" : code,
            "message" : message,
            "description" : description
        }]
    }

def validar_entero_positivo(valor, minimo, nombre):
    if valor is None or str(valor).strip == "":
        raise ValueError(construir_error_api(
            code=const.ERROR_CODE_EMPTY_VALUE,
            message='El campo no puede estar vacio',
            description=f"El campo '{nombre}' no puede estar vacio"
        ))
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Parametro invalido',
            description=f"El campo '{nombre}' debe ser un numero entero"
        ))   
    if numero < const.ENTERO_POSITIVO_MINIMO:
        raise ValueError(construir_error_api(
            code=const.ERROR_CODE_INVALID_MIN_VALUE,
            message="Valor por debajo del minimo",
            description=f"'{nombre}' debe ser mayor o igual a '{minimo}', se recibio {valor}"
        ))
    return valor

"""
Esta funcion sirve para proteger rutas de la API, verifica si hay un id_usuario en la sesion activa
si esta logueado permite acceder: En caso de no estarlo, anula la peticion y devuelve error 401 (No autenticado)
"""
def login_requerido(funcion):
    @wraps(funcion)
    def verificar_sesion(*args, **kwargs):
        if "id_usuario" not in session:
            error = construir_error_api("NO_AUTENTICADO", "No autenticado", "Debe iniciar sesion para acceder")
            return jsonify(error), 401
        return funcion(*args, **kwargs)
    return verificar_sesion

"""
Verifica si el rol del usuario es admin
si esta logueado y es admin permite acceder: En caso de no estarlo, 
anula la peticion y devuelve error 403 (No autorizado)
"""

def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if session.get("id_usuario") is None:
            return jsonify({"error": "Debés iniciar sesión"}), 401

        if session.get("rol") != "admin":
            return jsonify({"error": "No tenés permisos de administrador"}), 403

        return func(*args, **kwargs)

    return wrapper
