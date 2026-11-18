from datetime import datetime


def leer_fecha(texto):
    if not isinstance(texto, str) or len(texto) != 10:
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date() #strptime convierte el texto en fecha
    except ValueError:
        return None


def validar(datos, es_creacion):
    if not isinstance(datos, dict):
        return "El cuerpo del pedido debe ser un JSON"

    if es_creacion or "nombre" in datos:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 150:
            return "El nombre es obligatorio y puede tener hasta 150 caracteres"

    if es_creacion or "imagen_url" in datos:
        imagen_url = datos.get("imagen_url")
        if not isinstance(imagen_url, str) or not imagen_url.strip() or len(imagen_url) > 500:
            return "La imagen es obligatoria y puede tener hasta 500 caracteres"

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

    return None


def validar_creacion(datos):
    return validar(datos, es_creacion=True)


def validar_modificacion(datos):
    return validar(datos, es_creacion=False)
