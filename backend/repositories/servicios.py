from db import (
    ejecutar_consulta,
    ejecutar_mutacion,
)

def obtener_servicios() -> list[dict]:
    sql = "SELECT * FROM productos"
    return ejecutar_consulta(sql)


def obtener_servicio_por_id(id_producto: int) -> dict | None:
    sql = "SELECT * FROM productos WHERE id_producto = %s"
    filas = ejecutar_consulta(sql, (id_producto,))
    return filas[0] if filas else None


def crear_servicio(nombre, tipo, descripcion, precio, activo):
    sql = "INSERT INTO productos (nombre, tipo, descripcion, precio, activo) VALUES (%s, %s, %s, %s, %s)"
    return ejecutar_mutacion(sql, (nombre, tipo, descripcion, precio, activo))


def actualizar_servicio(id_producto, nombre, tipo, descripcion, precio, activo):
    sql = "UPDATE productos SET nombre = %s, tipo = %s, descripcion = %s, precio = %s, activo = %s WHERE id_producto = %s"
    return ejecutar_mutacion(sql, (nombre, tipo, descripcion, precio, activo, id_producto))


def dar_de_baja_servicio(id_producto: int):
    sql = "UPDATE productos SET activo = FALSE WHERE id_producto = %s"
    return ejecutar_mutacion(sql, (id_producto,))

