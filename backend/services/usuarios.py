from werkzeug.security import generate_password_hash, check_password_hash #Importa funciones de la libreria Werkzeug para el cifrado y verificacion de contraseñas
from repositories import usuarios as usuarios_repository

def usuario_publico(usuario):
    return {
        "id_usuario":         usuario["id_usuario"],
        "nombre":             usuario["nombre"],
        "apellido":           usuario["apellido"],
        "email":              usuario["email"],
        "fecha_nacimiento":   usuario["fecha_nacimiento"],
        "rol":                usuario["rol"],
        "activo":             bool(usuario["activo"]),
    }

def registrar_usuario(nombre, apellido, email, fecha_nacimiento, contrasena):
    email = email.lower()

    if usuarios_repository.buscar_por_email(email):
        return None, ("EMAIL_DUPLICADO", "Email en uso", "El email que quieres usar, ya esta en uso")

    contrasena_hash = generate_password_hash(contrasena)
    id_nuevo = usuarios_repository.crear_usuario(nombre, apellido,email, fecha_nacimiento, contrasena_hash)
    usuario = usuarios_repository.buscar_por_id(id_nuevo)

    return usuario_publico(usuario), None


def autenticar_usuario(email, contrasena):
    usuario = usuarios_repository.buscar_por_email(email.lower())

    if not usuario or not check_password_hash(usuario["contrasena_hash"], contrasena):
        return None, ("CREDENCIALES_INVALIDAS","Credenciales invalidas","Email o contraseña incorrectos")

    if not usuario["activo"]:
        return None, ("CUENTA_DESACTIVADA","Cuenta desactivada", "La cuenta está desactivada")

    return usuario_publico(usuario), None