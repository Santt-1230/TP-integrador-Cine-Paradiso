from repositories import salas as salas_repository
from validators import salas as salas_validator

def listar_salas(id_local=None):
    id_local = salas_validator.validar_id_local(id_local)
    return salas_repository.listar_salas_por_local(id_local)

def listar_sala_id(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    return salas_repository.listar_sala_por_id(id_sala)

def crear_sala(datos):
    id_local=salas_validator.validar_id_local(datos.get('id_local'))
    numero_sala=salas_validator.validar_numero_sala(datos.get('numero_local'))
    capacidad=salas_validator.validar_capacidad(datos.get('capacidad'))
    return salas_repository.crear_sala_con_butacas(id_local, numero_sala, capacidad)