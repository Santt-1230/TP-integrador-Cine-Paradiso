from repositories.promociones import (
    obtener_promociones,
    obtener_promocion_por_id,
    crear_promocion as crear_promocion_repo,
    actualizar_promocion as actualizar_promocion_repo,
    dar_de_baja_promocion as dar_de_baja_promocion_repo,
)
from datetime import date


def calcular_estado_promocion(promocion):
    hoy = date.today()

    if not promocion["activa"]:
        return "Inactiva"

    if hoy < promocion["vigente_desde"]:
        return "Pendiente"

    if hoy > promocion["vigente_hasta"]:
        return "Vencida"

    return "Activa"


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
        promocion["estado"] = calcular_estado_promocion(promocion)
        if incluir_inactivas or promocion["estado"] == "Activa":
            resultado.append(formatear_fecha(promocion))
    return resultado


def listar_promocion_por_id(id_promocion):
    return formatear_fecha(obtener_promocion_por_id(id_promocion))


def crear_promocion(datos):
    tipo = datos["tipo"]

    cantidad_comprar = None
    cantidad_pagar = None
    porcentaje = None
    monto_descuento = None

    if tipo == "nxm":
        cantidad_comprar = datos.get("cantidad_comprar")
        cantidad_pagar = datos.get("cantidad_pagar")

    elif tipo == "porcentaje":
        porcentaje = datos.get("porcentaje")

    elif tipo == "monto_fijo":
        monto_descuento = datos.get("monto_descuento")

    resultado = crear_promocion_repo(
        datos["nombre"],
        datos.get("descripcion"),
        datos.get("imagen_url"),
        datos["vigente_desde"],
        datos["vigente_hasta"],
        datos.get("activa", True),
        tipo,
        cantidad_comprar,
        cantidad_pagar,
        porcentaje,
        monto_descuento,
    )

    return formatear_fecha(obtener_promocion_por_id(resultado["id"]))


def actualizar_promocion(id_promocion, datos):
    actual = obtener_promocion_por_id(id_promocion)
    if actual is None:
        return None

    tipo = datos.get("tipo", actual["tipo"])

    if tipo == "nxm":
        cantidad_comprar = datos.get("cantidad_comprar", actual["cantidad_comprar"])
        cantidad_pagar = datos.get("cantidad_pagar", actual["cantidad_pagar"])
        porcentaje = None
        monto_descuento = None

    elif tipo == "porcentaje":
        cantidad_comprar = None
        cantidad_pagar = None
        porcentaje = datos.get("porcentaje", actual["porcentaje"])
        monto_descuento = None

    elif tipo == "monto_fijo":
        cantidad_comprar = None
        cantidad_pagar = None
        porcentaje = None
        monto_descuento = datos.get("monto_descuento", actual["monto_descuento"])

    actualizar_promocion_repo(
        id_promocion,
        datos.get("nombre", actual["nombre"]),
        datos.get("descripcion", actual["descripcion"]),
        datos.get("imagen_url", actual["imagen_url"]),
        datos.get("vigente_desde", actual["vigente_desde"]),
        datos.get("vigente_hasta", actual["vigente_hasta"]),
        datos.get("activa", actual["activa"]),
        tipo,
        cantidad_comprar,
        cantidad_pagar,
        porcentaje,
        monto_descuento,
    )

    return formatear_fecha(obtener_promocion_por_id(id_promocion))


def dar_de_baja_promocion(id_promocion):
    promocion = obtener_promocion_por_id(id_promocion)
    if promocion is None:
        return False
    dar_de_baja_promocion_repo(id_promocion)
    return True
