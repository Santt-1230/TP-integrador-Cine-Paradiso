def validar_peticion_cancelacion(datos: dict | None) -> tuple[bool, str | None]:
    if datos is None:
        return False, "El cuerpo de la petición debe ser un JSON válido"

    if "estado" not in datos:
        return False, "El campo 'estado' es obligatorio"

    estado = datos.get("estado")
    if estado != "cancelada":
        return False, f"El estado '{estado}' no es válido para esta operación. Solo se admite 'cancelada'"

    return True, None