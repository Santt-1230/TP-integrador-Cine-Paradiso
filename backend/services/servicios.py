from repositories.servicios import (
    obtener_servicios,
    obtener_servicio_por_id,
    crear_servicio as crear_servicio_repo,
    actualizar_servicio as actualizar_servicio_repo,
    dar_de_baja_servicio as dar_de_baja_servicio_repo,
)


def listar_servicios():
    servicios = obtener_servicios()
    activos = []
    for servicio in servicios:
        if servicio["activo"]:
            activos.append(servicio)
    return activos


def listar_servicio_por_id(id_producto):
    return obtener_servicio_por_id(id_producto) 


def crear_servicio(datos):
    resultado = crear_servicio_repo(
        datos["nombre"],
        datos["tipo"],
        datos.get("descripcion"),
        datos["precio"],
        datos.get("activo", True),
    )
    return obtener_servicio_por_id(resultado["id"])


def actualizar_servicio(id_producto, datos):
    actual = obtener_servicio_por_id(id_producto)
    if actual is None:
        return None
    actualizar_servicio_repo(
        id_producto,
        datos.get("nombre", actual["nombre"]),
        datos.get("tipo", actual["tipo"]),
        datos.get("descripcion", actual["descripcion"]),
        datos.get("precio", actual["precio"]),
        datos.get("activo", actual["activo"]),
    )
    return obtener_servicio_por_id(id_producto)


def dar_de_baja_servicio(id_producto):
    servicio = obtener_servicio_por_id(id_producto)
    if servicio is None:
        return False
    dar_de_baja_servicio_repo(id_producto)
    return True
