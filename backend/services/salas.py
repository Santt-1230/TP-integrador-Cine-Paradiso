from repositories import salas as salas_repository
from validators import salas as salas_validator

def listar_salas(id_local=None):
    id_local = salas_validator.validar_id_local(id_local)
    return salas_repository.listar_salas(id_local)