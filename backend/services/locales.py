from repositories import locales as locales_repository
from validators import locales as locales_validators
from services import salas as salas_services
from validators import salas as salas_validators
from utils import construir_error_api
from constants import ERROR_CODE_LOCAL_NOT_FOUND, ERROR_CODE_LOCAL_INACTIVE

def listar_locales():
    return locales_repository.listar_locales_activos()

def obtener_local(id_local):
    local = locales_repository.obtener_local_id(id_local)
    if local is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_LOCAL_NOT_FOUND,
            message='Local no encontrado',
            description=f"No existe un local con el ID '{id_local}'."
        ))
    return local

def obtener_local_activo(id_local):
    local = obtener_local(id_local)
    if not local['activo']:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_LOCAL_INACTIVE,
            message='Local inactivo',
            description=f"El local '{id_local}' esta inactivo"
        ))
    return local

def resumen_salas(id_local, estado):
    id_local = locales_validators.validar_filtro_local(id_local)
    estado = salas_validators.validar_filtro_estado(estado)

    todos = listar_locales()
    a_mostrar = todos if id_local is None else [obtener_local(id_local)]
    salas = salas_services.listar_salas(id_local, estado)

    return {
        'locales': armar_locales_con_salas(a_mostrar, salas),
        'todos_los_locales': armar_desplegable(todos),
        'salas_configuradas': len(salas),
        'filtros': {'estado': estado or 'todas', 'id_local': id_local},
    }


def armar_locales_con_salas(locales, salas):
    salas_por_local = {}
    for sala in salas:
        if sala['id_local'] not in salas_por_local:
            salas_por_local[sala['id_local']] = []
        salas_por_local[sala['id_local']].append(sala)

    resultado = []
    for local in locales:
        salas_del_local = salas_por_local.get(local['id_local'], [])
        total_butacas = 0
        for sala in salas_del_local:
            total_butacas += sala['capacidad']

        resultado.append({'id_local': local['id_local'], 'nombre': local['nombre'],
            'cantidad_salas': len(salas_del_local),'total_butacas': total_butacas,
            'salas': salas_del_local,
        })
    return resultado


def armar_desplegable(locales):
    desplegable = []
    for local in locales:
        desplegable.append({'id_local': local['id_local'], 'nombre': local['nombre']})
    return desplegable