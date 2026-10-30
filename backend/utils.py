from flask import jsonify
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

def validar_entero_positivo(valor, nombre):
    if valor is None or str(valor).strip == "":
        raise ValueError(f"{nombre} no puede estar vacio")
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} no puede estar vacio")   
    if numero < const.ENTERO_POSITIVO_MINIMO:
        raise ValueError(f"{nombre} debe ser mayor que cero")
    return
