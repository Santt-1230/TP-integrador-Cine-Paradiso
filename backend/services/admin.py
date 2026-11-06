from repositories import admin as admin_repository


def obtener_usuarios():
    usuarios = admin_repository.obtener_usuarios()
    return usuarios


def obtener_usuario_por_id(id):
    usuario = admin_repository.obtener_usuario_por_id(id)
    return usuario


def actualizar_usuario(id, nombre, email, rol):
    admin_repository.actualizar_usuario(id, nombre, email, rol)