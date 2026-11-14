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
    return ut.validar_entero_positivo(
        capacidad, const.ENTERO_POSITIVO_MINIMO, 'capacidad'
        )

def validar_actualizacion_sala(datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Datos invalidos',
            description="Ingresa numero_sala o estado"
        ))
    for campo in datos:
        if campo not in ('numero_sala', 'estado'):
            raise ValueError(ut.construir_error_api(
                code=const.ERROR_CODE_INVALID_PARAMETER,
                message='Campo no modificable',
                description=f"No se puede modificar el campo '{campo}'"
            ))
    cambios = {}
    if 'numero_sala' in datos:
        cambios['numero_sala'] = validar_numero_sala(datos['numero_sala'])
    if 'estado' in datos:
        if datos['estado'] not in ('activa', 'inactiva'):
            raise ValueError(ut.construir_error_api(
                code=const.ERROR_CODE_INVALID_PARAMETER,
                message='Estado invalido',
                description='El estado debe ser activa o inactiva'
            ))
        cambios['estado'] = datos['estado']
    return cambios