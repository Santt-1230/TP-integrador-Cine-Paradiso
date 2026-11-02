TIPOS_VALIDOS = ("comida", "bebida", "estacionamiento", "vip")

def validar(datos, es_creacion):
    if not isinstance(datos, dict):
        return "El cuerpo del pedido debe ser un JSON"

    if es_creacion or "nombre" in datos:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 100:
            return "El nombre es obligatorio y puede tener hasta 100 caracteres"

    if es_creacion or "tipo" in datos:
        if datos.get("tipo") not in TIPOS_VALIDOS:
            return "El tipo debe ser: comida, bebida, estacionamiento o vip"

    if es_creacion or "precio" in datos:
        precio = datos.get("precio")
        if isinstance(precio, bool) or not isinstance (precio, (int, float)) or precio < 0:
            return "El precio debe ser un numero mayor o igual a 0"

    if "descripcion" in datos:
        descripcion = datos.get("descripcion")
        if descripcion is not None and (not isinstance(descripcion, str) or len(descripcion) > 255):
            return "La descripcion debe ser texto de hasta 255 caracteres"

    if "activo" in datos and not isinstance(datos["activo"], bool):
        return "Activo debe ser verdadero o falso"

    return None

def validar_creacion(datos):
    return validar(datos, es_creacion=True)

def validar_modificacion(datos):
    return validar(datos, es_creacion=False)
