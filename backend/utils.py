from flask import jsonify, session
from functools import wraps
import logging
import constants as const
from db import ejecutar_consulta

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

def construir_error_db():
    return construir_error_api(
        code=const.ERROR_CODE_DATABASE_ERROR,
        message=const.ERROR_MESSAGE_DATABASE_ERROR,
        description=const.ERROR_DESCRIPTION_DATABASE_ERROR
    )

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


def admin_requerido(funcion):
    @wraps(funcion)
    @login_requerido
    def verificar_rol(*args, **kwargs):
        filas = ejecutar_consulta(
            "SELECT rol, activo FROM usuarios WHERE id_usuario = %s",
            (session["id_usuario"],),
        )
        if not filas or filas[0]["rol"] != const.ROL_ADMINISTRADOR or not filas[0]["activo"]:
            error = construir_error_api(const.ERROR_CODE_FORBIDDEN, "Acceso denegado",
                                        "Se requiere el rol de administrador")
            return jsonify(error), 403
        return funcion(*args, **kwargs)
    return verificar_rol

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
