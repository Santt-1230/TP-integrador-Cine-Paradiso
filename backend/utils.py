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

def rol_requerido(*roles):
    def decorador(funcion):
        @wraps(funcion)
        def verificar_rol(*args, **kwargs):
            if session.get("rol") not in roles:
                error = construir_error_api("PERMISO_DENEGADO", "Permiso denegado", "No tienes permisos para acceder")
                return jsonify(error), 403
            return funcion(*args, **kwargs)
        return verificar_rol
    return decorador