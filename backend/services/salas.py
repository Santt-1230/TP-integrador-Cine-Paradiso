from repositories import salas as salas_repository
from repositories import locales as locales_repository
from validators import salas as salas_validator
from services  import funciones as services_funciones
import utils as ut
import constants as const
def listar_salas(id_local=None):
    if id_local is not None:
        id_local = salas_validator.validar_id_local(id_local)
    return salas_repository.listar_salas_por_local(id_local)

def listar_sala_id(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    return salas_repository.listar_sala_por_id(id_sala)

def crear_sala(datos):
    id_local=salas_validator.validar_id_local(datos.get('id_local'))
    numero_sala=salas_validator.validar_numero_sala(datos.get('numero_sala'))
    capacidad=salas_validator.validar_capacidad(datos.get('capacidad'))
    local = locales_repository.obtener_local_id(id_local)
    if local is None:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_LOCAL_NOT_FOUND,
            message='Local no encontrado',
            description=f"No existe un local con el ID '{id_local}'."
        ))
    if not local['activo']:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_LOCAL_INACTIVE,
            message='Local inactivo',
            description=f"No se puede crear una sala en el local '{id_local}'"
        ))
    if salas_repository.existe_sala_crear(id_local, numero_sala):
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_SALA_CONFLICT,
            message='Numero de sala ocupado',
            description=f"Ya existe una sala con el numero '{numero_sala}' en el local '{id_local}'"
        ))
    id_sala = salas_repository.crear_sala_con_butacas(id_local, numero_sala, capacidad)
    return salas_repository.listar_sala_por_id(id_sala)

def obtener_butacas_sala(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    sala = salas_repository.listar_sala_por_id(id_sala)
    if sala is None:
        return None
    return salas_repository.obtener_butacas(id_sala)

def actualizar_sala(id_sala, datos):
    id_sala = salas_validator.validar_id_sala(id_sala)
    sala = salas_repository.listar_sala_por_id(id_sala)
    cambios = salas_validator.validar_actualizacion_sala(datos)
    if sala is None:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_SALA_NOT_FOUND,
            message='Sala no encontrada',
            description=f"No existe una sala con el ID '{id_sala}'."
        ))
    for campo in list(cambios):
        if sala[campo] == cambios[campo]:
            del cambios[campo]
    if not cambios:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_INVALID_PARAMETER,
            message='Sin cambios',
            description='Debes modificar al menos un campo de la sala'
        ))
    if 'numero_sala' in cambios:
        numero_nuevo = cambios['numero_sala']
        if salas_repository.existe_sala_editar(sala['id_local'], numero_nuevo, id_sala):
            raise ValueError(ut.construir_error_api(
                code=const.ERROR_CODE_SALA_CONFLICT,
                message='Numero de sala ocupado',
                description=f"Ya existe una sala con el numero {numero_nuevo} en el local {sala['id_local']}."
            ))
    
    return salas_repository.actualizar_sala(id_sala, cambios)


def desactivar_sala(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    sala = salas_repository.listar_sala_por_id(id_sala)
    if sala is None:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_SALA_NOT_FOUND,
            message='Sala no encontrada',
            description=f"No existe una sala con el ID '{id_sala}'"
        ))
    
    funciones = services_funciones.listar_funciones_por_sala(id_sala)
    if funciones:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_SALA_CONFLICT,
            message='Sala reservada',
            description=f"La sala '{id_sala}' tiene {len(funciones)} funciones programadas"
        ))
    return salas_repository.desactivar_sala(id_sala)

def listar_salas_activas(id_local):
    id_local = salas_validator.validar_id_local(id_local)
    local = locales_repository.obtener_local_id(id_local)

    if local is None or not local['activo']:
        raise ValueError(ut.construir_error_api(
            code=const.ERROR_CODE_LOCAL_NOT_FOUND,
            message='Local no encontrado',
            description=f"No existe un local activo con el ID '{id_local}'"
        ))
    return salas_repository.listar_salas_activas(id_local)