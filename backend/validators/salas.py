import re
import utils as ut
import constants as const

def validar_id_local(id_local)->int:
    if id_local is None:
        return None
    return ut.validar_entero_positivo(id_local, const.ENTERO_POSITIVO_MINIMO, "id_local")
