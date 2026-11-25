def validar_rol(rol):
    roles_permitidos = ["cliente", "administrador"]

    return rol in roles_permitidos


def validar_actualizacion_usuario(data):

    if not isinstance(data, dict):
        return None, "Faltan datos requeridos"

    nombre = str(data.get("nombre") or "").strip()
    email = str(data.get("email") or "").strip()
    rol = str(data.get("rol") or "").strip()

    if not nombre or not email or not rol:
        return None, "Faltan datos requeridos"

    if not validar_rol(rol):
        return None, "El rol no es válido"

    return {
        "nombre": nombre,
        "email": email,
        "rol": rol
    }, None