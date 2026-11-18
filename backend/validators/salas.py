import utils as ut
from constants import (
    ENTERO_POSITIVO_MINIMO, 
    CAPACIDAD_MAXIMA, 
    ERROR_CODE_INVALID_PARAMETER, 
    BUTACAS_POR_FILA)
import string

def validar_id_local(id_local)->int:
    if id_local is None:
        return None
    return ut.validar_entero_positivo(
        id_local, ENTERO_POSITIVO_MINIMO, 'id_local'
    )

def validar_id_sala(id_sala)->int:
    return ut.validar_entero_positivo(
        id_sala, ENTERO_POSITIVO_MINIMO, 'id_sala'
    )

def validar_numero_sala(numero_sala)->int:
    return ut.validar_entero_positivo(
        numero_sala, ENTERO_POSITIVO_MINIMO, 'numero_sala'
        )

def validar_capacidad(capacidad)->int:
    capacidad = ut.validar_entero_positivo(
        capacidad, ENTERO_POSITIVO_MINIMO, 'capacidad'
    )
    if capacidad > CAPACIDAD_MAXIMA:
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Capacidad invalida',
            description=f'La capacidad no puede superar {CAPACIDAD_MAXIMA} butacas'
        ))

    return capacidad

def validar_estado(estado)->str:
    if estado not in ('activa', 'inactiva'):
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Estado invalido',
            description='El estado debe ser activa o inactiva'
        ))
    return estado

def validar_filtro_estado(estado)->str:
    if estado is None or estado == '':
        return None
    return validar_estado(estado)

def error_filas(descripcion):
    return ValueError(ut.construir_error_api(
        code=ERROR_CODE_INVALID_PARAMETER,
        message='Filas invalidas',
        description=descripcion
    ))

def validar_filas(filas)->list:
    if not isinstance(filas, list) or not filas:
        raise error_filas('Ingresa al menos una fila')

    resultado = []
    total = 0
    letra_anterior = None

    for item in filas:
        if not isinstance(item, dict):
            raise error_filas('Cada fila debe tener letra y cantidad')

        fila = item.get('fila')
        if not isinstance(fila, str) or len(fila) != ENTERO_POSITIVO_MINIMO or fila not in string.ascii_uppercase:
            raise error_filas('La fila debe ser una letra mayuscula de la A a la Z')

        if letra_anterior is not None and ord(fila) != ord(letra_anterior) + ENTERO_POSITIVO_MINIMO:
            raise error_filas('Las filas deben ser consecutivas, sin repetir ni saltear letras')
        
        cantidad = ut.validar_entero_positivo(item.get('cantidad'), ENTERO_POSITIVO_MINIMO, 'cantidad')
        if cantidad > BUTACAS_POR_FILA:
            raise error_filas(f'Cada fila puede tener hasta {BUTACAS_POR_FILA} butacas')

        total += cantidad
        letra_anterior = fila
        resultado.append({'fila':fila, 'cantidad':cantidad})

    if total > CAPACIDAD_MAXIMA:
        raise error_filas(f'La sala no puede superar las {CAPACIDAD_MAXIMA} butacas')
    return resultado


def validar_actualizacion_sala(datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Datos invalidos',
            description="Ingresa numero_sala o estado"
        ))
    for campo in datos:
        if campo not in ('numero_sala', 'estado', 'capacidad'):
            raise ValueError(ut.construir_error_api(
                code=ERROR_CODE_INVALID_PARAMETER,
                message='Campo no modificable',
                description=f"No se puede modificar el campo '{campo}'"
            ))
    cambios = {}
    if 'numero_sala' in datos:
        cambios['numero_sala'] = validar_numero_sala(datos['numero_sala'])
    if 'estado' in datos:
        cambios['estado'] = validar_estado(datos['estado'])
    if 'capacidad' in datos:
        cambios['capacidad'] = validar_capacidad(datos['capacidad'])  
    if 'filas' in datos:
        cambios['filas'] = validar_filas(datos['filas'])
    return cambios

