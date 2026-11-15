import utils as ut
import constants as const

def validar_id_local(id_local)->int:
    if id_local is None:
        return None
    return ut.validar_entero_positivo(
        id_local, const.ENTERO_POSITIVO_MINIMO, 'id_local'
    )

def validar_id_sala(id_sala)->int:
    return ut.validar_entero_positivo(
        id_sala, const.ENTERO_POSITIVO_MINIMO, 'id_sala'
    )

def validar_numero_sala(numero_sala)->int:
    return ut.validar_entero_positivo(
        numero_sala, const.ENTERO_POSITIVO_MINIMO, 'numero_sala'
        )

def validar_capacidad(capacidad)->int:
    capacidad = ut.validar_entero_positivo(
        capacidad, const.ENTERO_POSITIVO_MINIMO, 'capacidad'
    )
    if capacidad > const.CAPACIDAD_MAXIMA:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Capacidad invalida',
            description=f'La capacidad no puede superar {const.CAPACIDAD_MAXIMA} butacas'
        ))

    return capacidad

def validar_estado(estado)->str:
    if estado not in ('activa', 'inactiva'):
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Estado invalido',
            description='El estado debe ser activa o inactiva'
        ))
    return estado

def validar_filtro_estado(estado)->str:
    if estado is None or estado == '':
        return None
    return validar_estado(estado)

def validar_actualizacion_sala(datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Datos invalidos',
            description="Ingresa numero_sala o estado"
        ))
    for campo in datos:
        if campo not in ('numero_sala', 'estado', 'capacidad'):
            raise ValueError(ut.construir_error_api(
                code=const.ERROR_CODE_INVALID_PARAMETER,
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
    
    return cambios

