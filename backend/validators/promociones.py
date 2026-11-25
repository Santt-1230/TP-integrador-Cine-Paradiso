from datetime import datetime
from decimal import Decimal

TIPOS_VALIDOS = ("nxm", "porcentaje", "monto_fijo")

def leer_fecha(texto):
    if not isinstance(texto, str) or len(texto) != 10:
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date() 
    except ValueError:
        return None


def validar(datos, es_creacion):
    if not isinstance(datos, dict):
        return "El cuerpo del pedido debe ser un JSON"

    if es_creacion or "nombre" in datos:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 150:
            return "El nombre es obligatorio y puede tener hasta 150 caracteres"

    if "imagen_url" in datos:
        imagen_url = datos.get("imagen_url")
        if imagen_url is not None and (not isinstance(imagen_url, str) or not imagen_url.strip() or len(imagen_url) > 500):
            return "La imagen URL debe ser un texto y de hasta 500 caracteres"

    if "descripcion" in datos:
        descripcion = datos.get("descripcion")
        if descripcion is not None and (not isinstance(descripcion, str) or len(descripcion) > 300):
            return "La descripcion debe ser texto de hasta 300 caracteres"

    desde = None
    hasta = None
    
    if es_creacion or "vigente_desde" in datos:
        desde = leer_fecha(datos.get("vigente_desde"))
        if desde is None:
            return "La fecha de inicio debe tener el formato AAAA-MM-DD (por ejemplo 2026-11-20)"

    if es_creacion or "vigente_hasta" in datos:
        hasta = leer_fecha(datos.get("vigente_hasta"))
        if hasta is None:
            return "La fecha final debe tener el formato AAAA-MM-DD (por ejemplo 2026-12-31)"
    
    if desde is not None and hasta is not None and hasta < desde:
        return "La fecha final no puede ser anterior a la de inicio"

    if "activa" in datos and not isinstance(datos["activa"], bool):
        return "Activa debe ser verdadero o falso"
    
    if es_creacion or "tipo" in datos:
        if datos.get("tipo") not in TIPOS_VALIDOS:
            return "El tipo debe ser nxm, porcentaje o monto_fijo"

    tipo = datos.get("tipo")

    if tipo == "nxm":
        comprar = datos.get("cantidad_comprar")
        pagar = datos.get("cantidad_pagar")

        if not isinstance(comprar, int) or isinstance(comprar, bool) or comprar <= 0:
            return "La cantidad a comprar debe ser un entero mayor a 0"

        if not isinstance(pagar, int) or isinstance(pagar, bool) or pagar <= 0:
            return "La cantidad a pagar debe ser un entero mayor a 0"

        if pagar > comprar:
            return "La cantidad a pagar no puede superar la cantidad a comprar"

    elif tipo == "porcentaje":
        porcentaje = datos.get("porcentaje")

        if isinstance(porcentaje, bool) or not isinstance(porcentaje, (int, float, Decimal)) or not 0 < porcentaje < 100:
            return "El porcentaje debe ser un número mayor a 0 y menor a 100"

    elif tipo == "monto_fijo":
        monto = datos.get("monto_descuento")

        if isinstance(monto, bool) or not isinstance(monto, (int, float, Decimal)) or monto <= 0:
            return "El monto de descuento debe ser mayor a 0"

    return None


def validar_creacion(datos):
    return validar(datos, es_creacion=True)


def validar_modificacion(datos):
    return validar(datos, es_creacion=False)
