from flask import jsonify, session
from functools import wraps

def construir_error_api(code:str, message:str, description:str, level:str = 'error')->dict:
    return {
        'errors' :[{
            "error" : level,
            "code" : code,
            "message" : message,
            "description" : description
        }]
    }

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