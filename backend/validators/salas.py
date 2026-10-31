import re
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