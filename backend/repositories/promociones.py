from db import (
    ejecutar_consulta,
    ejecutar_mutacion,
)

def obtener_promociones() -> list[dict]:
    sql = "SELECT * FROM promociones"
    return ejecutar_consulta(sql)


def obtener_promocion_por_id(id_promocion: int) -> dict | None:
    sql = "SELECT * FROM promociones WHERE id_promocion = %s"
    filas = ejecutar_consulta(sql, (id_promocion,))
    return filas[0] if filas else None


def crear_promocion(nombre, descripcion, imagen_url, vigente_desde, vigente_hasta, activa):
    sql = "INSERT INTO promociones (nombre, descripcion, imagen_url, vigente_desde, vigente_hasta, activa) VALUES (%s, %s, %s, %s, %s, %s)"
    return ejecutar_mutacion(sql, (nombre, descripcion, imagen_url, vigente_desde, vigente_hasta, activa))


def actualizar_promocion(id_promocion, nombre, descripcion, imagen_url, vigente_desde, vigente_hasta, activa):
    sql = "UPDATE promociones SET nombre = %s, descripcion = %s, imagen_url = %s, vigente_desde = %s, vigente_hasta = %s, activa = %s WHERE id_promocion = %s"
    return ejecutar_mutacion(sql, (nombre, descripcion, imagen_url, vigente_desde, vigente_hasta, activa, id_promocion))


def dar_de_baja_promocion(id_promocion: int):
    sql = "UPDATE promociones SET activa = FALSE WHERE id_promocion = %s"
    return ejecutar_mutacion(sql, (id_promocion,))