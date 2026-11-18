from datetime import timedelta

import mysql.connector

import constants as const
from db import ejecutar_consulta, ejecutar_mutacion, obtener_conexion, transaccion


def finalizar_funciones_vencidas():
    """Marca como finalizados los turnos programados cuya hora de fin ya pasó."""
    sql = (
        "UPDATE funciones SET estado = 'finalizada' "
        "WHERE estado = 'programada' AND fecha_hora_fin <= NOW()"
    )
    return ejecutar_mutacion(sql)


def listar_funciones(pelicula_id=None, local_id=None, fecha=None, incluir_canceladas=False, id_sala = None):
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
        ", EXISTS (SELECT 1 FROM compras c "
        "WHERE c.id_funcion = f.id_funcion LIMIT 1) AS tiene_compras "
        "FROM funciones f "
        "INNER JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN salas s ON s.id_sala = f.id_sala "
        "INNER JOIN locales l ON l.id_local = s.id_local "
        "WHERE 1 = 1"
    )
    parametros = []

    if not incluir_canceladas:
        sql += " AND f.estado = 'programada' AND f.fecha_hora_inicio > NOW() AND p.activo = TRUE"
    if pelicula_id is not None:
        sql += " AND f.id_pelicula = %s"
        parametros.append(pelicula_id)
    if local_id is not None:
        sql += " AND s.id_local = %s"
        parametros.append(local_id)
    if fecha is not None:
        sql += " AND DATE(f.fecha_hora_inicio) = %s"
        parametros.append(fecha)
    if id_sala is not None:
        sql += " AND f.id_sala = %s"
        parametros.append(id_sala)
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


def pelicula_vigente_en(id_pelicula, fecha):
    """True si la fecha cae dentro de cartelera_desde/cartelera_hasta (NULL = sin limite)."""
    filas = ejecutar_consulta(
        "SELECT id_pelicula FROM peliculas WHERE id_pelicula = %s "
        "AND (cartelera_desde IS NULL OR cartelera_desde <= %s) "
        "AND (cartelera_hasta IS NULL OR cartelera_hasta >= %s)",
        (id_pelicula, fecha.date(), fecha.date()),
    )
    return bool(filas)


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


def eliminar_funcion_cancelada(id_funcion):
    with transaccion() as cursor:
        cursor.execute(
            "SELECT estado FROM funciones WHERE id_funcion = %s FOR UPDATE",
            (id_funcion,),
        )
        funcion = cursor.fetchone()
        if not funcion:
            return "no_encontrada"
        if funcion["estado"] != "cancelada":
            return "no_cancelada"

        cursor.execute(
            "SELECT id_compra FROM compras WHERE id_funcion = %s LIMIT 1",
            (id_funcion,),
        )
        if cursor.fetchone():
            return "con_compras"

        cursor.execute(
            "DELETE FROM funciones WHERE id_funcion = %s",
            (id_funcion,),
        )
    return "eliminada"


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


def reservar_butacas(id_usuario, id_funcion, id_butacas):
    conexion = obtener_conexion()
    cursor = None
    marcadores = ", ".join(["%s"] * len(id_butacas))

    try:
        cursor = conexion.cursor(dictionary=True)
        conexion.start_transaction()

        cursor.execute(
            "SELECT id_sala, precio_entrada, estado, fecha_hora_inicio "
            "FROM funciones WHERE id_funcion = %s FOR UPDATE",
            (id_funcion,),
        )
        funcion = cursor.fetchone()
        if not funcion:
            conexion.rollback()
            return None, (404, "FUNCION_NO_ENCONTRADA", "Función no encontrada", "No existe ese ID de función")

        cursor.execute(
            "SELECT fecha_hora_inicio <= NOW() AS ya_iniciada "
            "FROM funciones WHERE id_funcion = %s",
            (id_funcion,),
        )
        fecha_pasada = cursor.fetchone()["ya_iniciada"]
        if funcion["estado"] != "programada" or fecha_pasada:
            conexion.rollback()
            return None, (409, "FUNCION_NO_DISPONIBLE", "Función no disponible", "La función está cancelada, finalizada o ya comenzó")

        cursor.execute(
            f"SELECT id_butaca FROM butacas WHERE id_sala = %s "
            f"AND id_butaca IN ({marcadores}) FOR UPDATE",
            (funcion["id_sala"], *id_butacas),
        )
        asientos_validos = {fila["id_butaca"] for fila in cursor.fetchall()}
        if asientos_validos != set(id_butacas):
            conexion.rollback()
            return None, (400, "BUTACAS_INVALIDAS", "Butacas inválidas", "Alguna butaca no pertenece a la sala de esta función")

        cursor.execute(
            "UPDATE compras SET estado = 'expirada' "
            "WHERE estado = 'pendiente' AND expira_en <= NOW()"
        )
        cursor.execute(
            "UPDATE entradas e INNER JOIN compras c ON c.id_compra = e.id_compra "
            "SET e.estado = 'cancelada' WHERE c.estado = 'expirada' "
            "AND e.estado = 'reservada'"
        )

        cursor.execute(
            f"SELECT e.id_butaca FROM entradas e "
            f"INNER JOIN compras c ON c.id_compra = e.id_compra "
            f"WHERE e.id_funcion = %s AND e.id_butaca IN ({marcadores}) "
            f"AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
            f"AND (c.estado = 'confirmada' OR "
            f"(c.estado = 'pendiente' AND c.expira_en > NOW()))",
            (id_funcion, *id_butacas),
        )
        if cursor.fetchall():
            conexion.rollback()
            return None, (409, "BUTACA_NO_DISPONIBLE", "Butaca no disponible", "Una o más butacas ya están reservadas o vendidas")

        cursor.execute(
            "INSERT INTO compras (id_usuario, id_funcion, estado, expira_en, total) "
            "VALUES (%s, %s, 'pendiente', DATE_ADD(NOW(), INTERVAL 10 MINUTE), %s)",
            (id_usuario, id_funcion, funcion["precio_entrada"] * len(id_butacas)),
        )
        id_compra = cursor.lastrowid

        for id_butaca in id_butacas:
            cursor.execute(
                "INSERT INTO entradas (id_compra, id_funcion, id_butaca, precio_unitario, estado) "
                "VALUES (%s, %s, %s, %s, 'reservada')",
                (id_compra, id_funcion, id_butaca, funcion["precio_entrada"]),
            )

        cursor.execute("SELECT expira_en FROM compras WHERE id_compra = %s", (id_compra,))
        expira_en = cursor.fetchone()["expira_en"].isoformat(sep=" ", timespec="seconds")
        conexion.commit()
        return {"id_compra": id_compra, "id_funcion": id_funcion, "estado": "pendiente", "expira_en": expira_en}, None
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None, (409, "BUTACA_NO_DISPONIBLE", "Butaca no disponible", "Una o más butacas ya fueron reservadas por otra compra")
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
