from repositories.promociones import obtener_promociones


def listar_promociones():
    activas = []
    for promocion in obtener_promociones():
        if promocion["activo"]:
            activas.append(promocion)
    return activas