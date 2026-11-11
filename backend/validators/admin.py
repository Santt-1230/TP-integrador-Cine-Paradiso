
def validar_rol(rol):
    roles_permitidos = ["cliente", "admin"]

    return rol in roles_permitidos


def validar_actualizacion_usuario(nombre=None, email=None, rol=None):

    if nombre is not None:
        if not nombre.strip():
            return False

    if email is not None:
        if not email.strip():
            return False

    if rol is not None:
        if not validar_rol(rol):
            return False

    return True