from repositories import salas as salas_repository
from repositories import locales as locales_repository
from validators import salas as salas_validator
from services  import funciones as services_funciones
from services import locales as locales_services
from utils import construir_error_api
from constants import (ERROR_CODE_SALA_CONFLICT, ERROR_CODE_LOCAL_NOT_FOUND, 
    ERROR_CODE_INVALID_PARAMETER, ERROR_CODE_SALA_NOT_FOUND)

def obtener_sala_existente(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    sala = salas_repository.listar_sala_por_id(id_sala)
    if sala is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SALA_NOT_FOUND,
            message='Sala no encontrada',
            description=f"No existe una sala con el ID '{id_sala}'."
        ))
    return sala


def validar_programacion_sala(id_sala):
    funciones = services_funciones.listar_funciones_por_sala(id_sala)
    if funciones:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SALA_CONFLICT,
            message='Sala reservada',
            description=f"La sala '{id_sala}' tiene {len(funciones)} funciones programadas"
        ))

def obtener_filas_sala(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    if salas_repository.listar_sala_por_id(id_sala) is None:
        return None
    return salas_repository.listar_filas_sala(id_sala)

def listar_salas(id_local=None, estado=None):
    if id_local == '':
        id_local = None
    if id_local is not None:
        id_local = salas_validator.validar_id_local(id_local)
    estado = salas_validator.validar_filtro_estado(estado)

    locales_activos = locales_repository.listar_locales_activos()

    locales_a_mostrar = []
    for local in locales_activos:
        if id_local is None or local['id_local'] == id_local:
            locales_a_mostrar.append(local)

    if id_local is not None and not locales_a_mostrar:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_LOCAL_NOT_FOUND,
            message='Local no encontrado',
            description=f"No existe un Local con el id '{id_local}'"
        ))

    salas = salas_repository.listar_salas_por_local(id_local, estado)

    return {
        'locales': locales_services.armar_locales_con_salas(locales_a_mostrar, salas),
        'todos_los_locales': locales_services.armar_desplegable(locales_activos),
        'salas_configuradas': len(salas),
        'filtros': {'estado': estado or 'todas', 'id_local': id_local},
    }
def listar_sala_id(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    return salas_repository.listar_sala_por_id(id_sala)

def crear_sala(datos):
    sala = salas_validator.validar_creacion_sala(datos)
    locales_services.obtener_local_activo(sala['id_local'])

    if salas_repository.existe_sala_crear(sala['id_local'], sala['numero_sala']):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SALA_CONFLICT,
            message='Numero de sala ocupado',
            description=f"Ya existe una sala con el numero '{sala['numero_sala']}' en el local '{sala['id_local']}'"
        ))

    return salas_repository.crear_sala(
        sala['id_local'], sala['numero_sala'], sala['filas'])

def obtener_butacas_sala(id_sala):
    id_sala = salas_validator.validar_id_sala(id_sala)
    sala = salas_repository.listar_sala_por_id(id_sala)
    if sala is None:
        return None
    return salas_repository.obtener_butacas(id_sala)



def actualizar_sala(id_sala, datos):
    sala = obtener_sala_existente(id_sala)
    id_sala = sala['id_sala']
    cambios = salas_validator.validar_actualizacion_sala(datos)

    for campo in list(cambios):
        if campo == 'filas':
            if cambios['filas'] == salas_repository.listar_filas_sala(id_sala):
                del cambios['filas']
        elif sala[campo] == cambios[campo]:
            del cambios[campo]

    if not cambios:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Sin cambios',
            description='Debes modificar al menos un campo de la sala'
        ))

    if cambios.get('estado') == 'inactiva':
        validar_programacion_sala(id_sala)

    if 'numero_sala' in cambios:
        numero_nuevo = cambios['numero_sala']
        if salas_repository.existe_sala_editar(sala['id_local'], numero_nuevo, id_sala):
            raise ValueError(construir_error_api(
                code=ERROR_CODE_SALA_CONFLICT,
                message='Numero de sala ocupado',
                description=(f"Ya existe una sala con el numero {numero_nuevo} "
                             f"en el local {sala['id_local']}.")
            ))

    sala_editada = salas_repository.actualizar_sala(id_sala, cambios)

    if sala_editada is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SALA_CONFLICT,
            message='Butacas con entrada activa',
            description='No se pueden quitar butacas con entradas futuras activas'
        ))

    return sala_editada



def desactivar_sala(id_sala):
    sala = obtener_sala_existente(id_sala)
    
    validar_programacion_sala(sala['id_sala'])
    return salas_repository.desactivar_sala(sala['id_sala'])

def listar_salas_activas(id_local):
    id_local = salas_validator.validar_id_local(id_local)
    local = locales_repository.obtener_local_id(id_local)

    if local is None or not local['activo']:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_LOCAL_NOT_FOUND,
            message='Local no encontrado',
            description=f"No existe un local activo con el ID '{id_local}'"
        ))
    return salas_repository.listar_salas_activas(id_local)

