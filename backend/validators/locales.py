from constants import ENTERO_POSITIVO_MINIMO
from utils import validar_entero_positivo

def validar_id_local(id_local) -> int:
    return validar_entero_positivo(
        id_local, ENTERO_POSITIVO_MINIMO, 'id_local'
    )

def validar_filtro_local(id_local) -> int | None:
    if id_local is None or id_local == '':
        return None
    return validar_id_local(id_local)