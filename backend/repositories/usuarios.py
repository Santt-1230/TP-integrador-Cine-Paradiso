from db import ejecutar_consulta, ejecutar_mutacion

def crear_usuario(nombre, apellido, email, fecha_nacimiento, contrasena_hash):
    sql = "INSERT INTO usuarios (nombre, apellido, email, fecha_nacimiento, contrasena_hash, rol) VALUES (%s, %s, %s, %s, %s, %s)",
    (nombre, apellido, email, fecha_nacimiento, contrasena_hash, "cliente")
    resultado = ejecutar_mutacion(sql, (nombre, apellido, email, fecha_nacimiento, contrasena_hash))
    return resultado["id"]


def buscar_por_email(email):
    sql = "SELECT * FROM usuarios WHERE email = %s"
    filas = ejecutar_consulta(sql, (email,))
    return filas[0] if filas else None


def buscar_por_id(id_usuario) -> dict | None:
    sql = "SELECT * FROM usuarios WHERE id_usuario = %s"
    filas = ejecutar_consulta(sql, (id_usuario,))
    return filas[0] if filas else None