from datetime import timedelta

import mysql.connector

import constants as const
from db import ejecutar_consulta, ejecutar_mutacion, obtener_conexion


def listar_funciones(pelicula_id=None, local_id=None, fecha=None, incluir_canceladas=False):
    sql = (
        "SELECT f.id_funcion, f.id_pelicula, p.nombre AS pelicula, "
        "f.id_sala, s.numero_sala, s.id_local, l.nombre AS local, "
        "f.fecha_hora_inicio, f.fecha_hora_fin, f.precio_entrada, f.estado "
        ", EXISTS (SELECT 1 FROM entradas e "
        "INNER JOIN compras c ON c.id_compra = e.id_compra "
        "WHERE e.id_funcion = f.id_funcion "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW())) LIMIT 1) "
        "AS tiene_entradas_activas "
        "FROM funciones f "
        "INNER JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN salas s ON s.id_sala = f.id_sala "
        "INNER JOIN locales l ON l.id_local = s.id_local "
        "WHERE 1 = 1"
    )
    parametros = []

    if not incluir_canceladas:
        sql += " AND f.estado = 'programada' AND f.fecha_hora_inicio > NOW()"
    if pelicula_id is not None:
        sql += " AND f.id_pelicula = %s"
        parametros.append(pelicula_id)
    if local_id is not None:
        sql += " AND s.id_local = %s"
        parametros.append(local_id)
    if fecha is not None:
        sql += " AND DATE(f.fecha_hora_inicio) = %s"
        parametros.append(fecha)

    sql += " ORDER BY f.fecha_hora_inicio"
    return ejecutar_consulta(sql, tuple(parametros))


def obtener_funcion(id_funcion):
    sql = (
        "SELECT f.id_funcion, f.id_pelicula, p.nombre AS pelicula, "
        "f.id_sala, s.numero_sala, s.id_local, l.nombre AS local, "
        "f.fecha_hora_inicio, f.fecha_hora_fin, f.precio_entrada, f.estado "
        ", EXISTS (SELECT 1 FROM entradas e "
        "INNER JOIN compras c ON c.id_compra = e.id_compra "
        "WHERE e.id_funcion = f.id_funcion "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW())) LIMIT 1) "
        "AS tiene_entradas_activas "
        "FROM funciones f "
        "INNER JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN salas s ON s.id_sala = f.id_sala "
        "INNER JOIN locales l ON l.id_local = s.id_local "
        "WHERE f.id_funcion = %s"
    )
    filas = ejecutar_consulta(sql, (id_funcion,))
    return filas[0] if filas else None


def obtener_duracion_pelicula(id_pelicula):
    filas = ejecutar_consulta(
        "SELECT duracion_min FROM peliculas WHERE id_pelicula = %s AND activo = TRUE",
        (id_pelicula,),
    )
    return filas[0]["duracion_min"] if filas else None


def sala_activa(id_sala):
    filas = ejecutar_consulta(
        "SELECT id_sala FROM salas WHERE id_sala = %s AND estado = 'activa'",
        (id_sala,),
    )
    return bool(filas)


def fecha_hora_pasada(fecha_hora):
    filas = ejecutar_consulta(
        "SELECT %s <= NOW() AS fecha_pasada",
        (fecha_hora,),
    )
    return bool(filas[0]["fecha_pasada"])


def funcion_tiene_entradas_activas(id_funcion):
    sql = (
        "SELECT e.id_entrada FROM entradas e "
        "INNER JOIN compras c ON c.id_compra = e.id_compra "
        "WHERE e.id_funcion = %s "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW())) "
        "LIMIT 1"
    )
    return bool(ejecutar_consulta(sql, (id_funcion,)))


def hay_solapamiento(id_sala, inicio, fin, ignorar_funcion=None):
    margen = timedelta(minutes=const.MINUTOS_ENTRE_FUNCIONES)
    inicio_con_margen = inicio - margen
    fin_con_margen = fin + margen

    sql = (
        "SELECT id_funcion FROM funciones "
        "WHERE id_sala = %s AND estado = 'programada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s"
    )
    parametros = [id_sala, fin_con_margen, inicio_con_margen]

    if ignorar_funcion is not None:
        sql += " AND id_funcion <> %s"
        parametros.append(ignorar_funcion)

    return bool(ejecutar_consulta(sql, tuple(parametros)))


def crear_funcion(id_pelicula, id_sala, inicio, fin, precio):
    sql = (
        "INSERT INTO funciones "
        "(id_pelicula, id_sala, fecha_hora_inicio, fecha_hora_fin, precio_entrada, estado) "
        "VALUES (%s, %s, %s, %s, %s, 'programada')"
    )
    resultado = ejecutar_mutacion(sql, (id_pelicula, id_sala, inicio, fin, precio))
    return resultado["id"]


def actualizar_funcion(id_funcion, campos):
    nombres = {
        "id_pelicula": "id_pelicula",
        "id_sala": "id_sala",
        "fecha_hora_inicio": "fecha_hora_inicio",
        "fecha_hora_fin": "fecha_hora_fin",
        "precio_entrada": "precio_entrada",
        "estado": "estado",
    }
    partes = []
    parametros = []

    for nombre, valor in campos.items():
        partes.append(f"{nombres[nombre]} = %s")
        parametros.append(valor)

    parametros.append(id_funcion)
    sql = "UPDATE funciones SET " + ", ".join(partes) + " WHERE id_funcion = %s"
    ejecutar_mutacion(sql, tuple(parametros))


def listar_butacas_funcion(id_funcion):
    sql = (
        "SELECT b.id_butaca, b.fila, b.numero, "
        "CASE WHEN c.id_compra IS NULL THEN 'disponible' ELSE 'ocupada' END AS estado "
        "FROM funciones f "
        "INNER JOIN butacas b ON b.id_sala = f.id_sala "
        "LEFT JOIN entradas e ON e.id_funcion = f.id_funcion "
        "AND e.id_butaca = b.id_butaca "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "LEFT JOIN compras c ON c.id_compra = e.id_compra "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW())) "
        "WHERE f.id_funcion = %s "
        "ORDER BY b.fila, b.numero"
    )
    return ejecutar_consulta(sql, (id_funcion,))



