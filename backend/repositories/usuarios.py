from db import obtener_conexion


def crear_usuario(nombre, apellido, email, fecha_nacimiento, contrasena_hash):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, apellido, email, fecha_nacimiento, contrasena_hash, rol) VALUES (%s, %s, %s, %s, %s, %s)",
        (nombre, apellido, email, fecha_nacimiento, contrasena_hash, "cliente"),)
    conexion.commit()
    id_nuevo = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_nuevo


def buscar_por_email(email):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado


def buscar_por_id(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario