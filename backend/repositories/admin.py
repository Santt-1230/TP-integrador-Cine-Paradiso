from db import obtener_conexion


def obtener_usuarios():

    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, nombre, email, rol
            FROM usuario
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
            FROM usuario
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
            UPDATE usuario
            SET nombre = %s, email = %s, rol = %s
            WHERE id_usuario = %s
        """, (nombre, email, rol, id))

        conexion.commit()

    finally:
        cursor.close()
        conexion.close()