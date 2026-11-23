from db import ejecutar_consulta, ejecutar_mutacion


def crear(id_usuario, texto, puntuacion, categoria=None):
    return ejecutar_mutacion(
        """INSERT INTO opiniones (id_usuario, texto, puntuacion, categoria)
        VALUES (%s, %s, %s, %s)""",
        (id_usuario, texto, puntuacion, categoria),
    )


def listar():
    return ejecutar_consulta(
        """SELECT o.id_opinion, o.texto, o.puntuacion, o.categoria, o.fecha_creacion,
               u.nombre, u.apellido, u.email
        FROM opiniones o
        JOIN usuarios u ON u.id_usuario = o.id_usuario
        ORDER BY o.fecha_creacion DESC"""
    )