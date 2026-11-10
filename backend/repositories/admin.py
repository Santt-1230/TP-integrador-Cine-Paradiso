from db import obtener_conexion


def obtener_usuarios():

    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, nombre, email, rol
            FROM usuarios
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()



def obtener_usuario_por_id(id):
    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, nombre, email, rol
            FROM usuarios
            WHERE id_usuario = %s
        """, (id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()


def actualizar_usuario(id, nombre, email, rol):
    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET nombre = %s, email = %s, rol = %s
            WHERE id_usuario = %s
        """, (nombre, email, rol, id))

        conexion.commit()

    finally:
        cursor.close()
        conexion.close()


def obtener_cantidad_peliculas_activas():
    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS cantidad
            FROM peliculas
            WHERE activa = TRUE
        """)

        resultado = cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()

    return resultado["cantidad"] if resultado else 0