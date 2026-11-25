from db import ejecutar_consulta, ejecutar_mutacion


def obtener_usuarios():

    sql = """
        SELECT id_usuario, nombre, email, rol
        FROM usuarios
    """

    return ejecutar_consulta(sql)


def obtener_usuario_por_id(id_usuario):

    sql = """
        SELECT id_usuario, nombre, email, rol
        FROM usuarios
        WHERE id_usuario = %s
    """

    usuarios = ejecutar_consulta(sql, (id_usuario,))

    return usuarios[0] if usuarios else None


def actualizar_usuario(id_usuario, nombre, email, rol):

    sql = """
        UPDATE usuarios
        SET nombre = %s,
            email = %s,
            rol = %s
        WHERE id_usuario = %s
    """

    return ejecutar_mutacion(
        sql,
        (nombre, email, rol, id_usuario)
    )

from db import ejecutar_consulta


def obtener_cantidad_peliculas_activas():

    sql = """
        SELECT COUNT(*) AS total
        FROM peliculas
        WHERE activo = TRUE
    """

    resultado = ejecutar_consulta(sql)

    return resultado[0]["total"] if resultado else 0


def obtener_cantidad_funciones_programadas():

    sql = """
        SELECT COUNT(*) AS total
        FROM funciones
        WHERE estado = 'programada'
    """

    resultado = ejecutar_consulta(sql)

    return resultado[0]["total"] if resultado else 0