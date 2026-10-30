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

