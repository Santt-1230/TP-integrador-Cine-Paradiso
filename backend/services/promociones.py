from repositories.promociones import obtener_promociones


def listar_promociones():
    activas = []
    for promocion in obtener_promociones():
        if promocion["activo"]:
            activos.append(promocion)
    return activas