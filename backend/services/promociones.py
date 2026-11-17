from repositories.promociones import (
    obtener_promociones,
    obtener_promocion_por_id,
    crear_promocion as crear_promocion_repo,
    actualizar_promocion as actualizar_promocion_repo,
    dar_de_baja_promocion as dar_de_baja_promocion_repo,
)


def formatear_fecha(promocion):
    if promocion is None:
        return None
    for campo in ("vigente_desde", "vigente_hasta"):
        if promocion[campo] is not None:
            promocion[campo] = promocion[campo].isoformat() #isoformat() convierte la fecha en formato AAAA-DD-MM
    return promocion


def listar_promociones(incluir_inactivas=False):
    promociones = obtener_promociones()
    resultado = []
    for promocion in promociones:
        if incluir_inactivas or promocion["activa"]:
            resultado.append(formatear_fecha(promocion))
    return resultado


def listar_promocion_por_id(id_promocion):
    return formatear_fecha(obtener_promocion_por_id(id_promocion))


def crear_promocion(datos):
    resultado = crear_promocion_repo(
        datos["nombre"],
        datos.get("descripcion"),
        datos.get("imagen_url"),
        datos["vigente_desde"],
        datos["vigente_hasta"],
        datos.get("activa", True),
    )
    return formatear_fecha(obtener_promocion_por_id(resultado["id"]))


def actualizar_promocion(id_promocion, datos):
    actual = obtener_promocion_por_id(id_promocion)
    if actual is None:
        return None
    actualizar_promocion_repo(
        id_promocion,
        datos.get("nombre", actual["nombre"]),
        datos.get("descripcion", actual["descripcion"]),
        datos.get("imagen_url", actual["imagen_url"]),
        datos.get("vigente_desde", actual["vigente_desde"]),
        datos.get("vigente_hasta", actual["vigente_hasta"]),
        datos.get("activa", actual["activa"]),
    )
    return formatear_fecha(obtener_promocion_por_id(id_promocion))


def dar_de_baja_promocion(id_promocion):
    promocion = obtener_promocion_por_id(id_promocion)
    if promocion is None:
        return False
    dar_de_baja_promocion_repo(id_promocion)
    return True
