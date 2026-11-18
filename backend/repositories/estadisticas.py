from db import ejecutar_consulta, ejecutar_mutacion
from datetime import datetime, timedelta


# =========================================================
# FECHAS
# =========================================================

def _marcar_funciones_finalizadas():
    # las estadísticas cuentan solo las finalizadas, y nada las marca al terminar
    ejecutar_mutacion(
        "UPDATE funciones SET estado = 'finalizada' "
        "WHERE estado = 'programada' AND fecha_hora_fin < NOW()",
        (),
    )


def obtener_fecha_inicio(periodo=30):

    if periodo is None:
        periodo = 30

    periodos_validos = (7, 30, 90, 365)

    try:
        dias = int(periodo)
    except (TypeError, ValueError):
        raise ValueError("El período debe ser 7, 30, 90 o 365 días")

    if dias not in periodos_validos:
        raise ValueError("El período seleccionado no es válido")

    return datetime.now() - timedelta(days=dias)


# =========================================================
# VENTAS TOTALES
# =========================================================

def obtener_ventas_totales(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COALESCE(SUM(c.total), 0) AS ventas_totales

        FROM compras AS c

        WHERE c.estado = 'confirmada'
            AND c.fecha_confirmacion >= %s
            AND c.fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_totales"] if resultado else 0


# =========================================================
# VENTAS DE ENTRADAS
# =========================================================

def obtener_ventas_entradas(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COUNT(e.id_entrada) AS ventas_entradas

        FROM compras AS c

        INNER JOIN entradas AS e
            ON c.id_compra = e.id_compra

        WHERE c.estado = 'confirmada'
            AND e.estado IN ('confirmada', 'utilizada')
            AND c.fecha_confirmacion >= %s
            AND c.fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_entradas"] if resultado else 0


# =========================================================
# VENTAS DE PRODUCTOS
# =========================================================

def obtener_ventas_productos(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COALESCE(
                SUM(cp.cantidad * cp.precio_unitario),
                0
            ) AS ventas_productos

        FROM compras AS c

        INNER JOIN compra_productos AS cp
            ON c.id_compra = cp.id_compra

        WHERE c.estado = 'confirmada'
            AND c.fecha_confirmacion >= %s
            AND c.fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_productos"] if resultado else 0


# =========================================================
# VENTAS POR GÉNERO
# =========================================================

def obtener_ventas_por_genero(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            g.nombre AS genero,

            COUNT(e.id_entrada) AS cantidad,

            SUM(e.precio_unitario) AS ventas_por_genero

        FROM compras AS c

        INNER JOIN entradas AS e
            ON c.id_compra = e.id_compra

        INNER JOIN funciones AS f
            ON e.id_funcion = f.id_funcion

        INNER JOIN peliculas AS p
            ON f.id_pelicula = p.id_pelicula

        INNER JOIN pelicula_genero AS pg
            ON p.id_pelicula = pg.id_pelicula

        INNER JOIN generos AS g
            ON pg.id_genero = g.id_genero

        WHERE c.estado = 'confirmada'
            AND e.estado IN ('confirmada', 'utilizada')
            AND c.fecha_confirmacion >= %s
            AND c.fecha_confirmacion <= NOW()

        GROUP BY g.id_genero, g.nombre

        ORDER BY cantidad DESC;
    """

    return ejecutar_consulta(consulta, (fecha_desde,))


# =========================================================
# CANCELACIONES
# =========================================================

def obtener_cancelaciones(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COUNT(c.id_compra) AS cancelaciones

        FROM compras AS c

        WHERE c.estado = 'cancelada'
            AND c.fecha_cancelacion IS NOT NULL
            AND c.fecha_cancelacion >= %s
            AND c.fecha_cancelacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["cancelaciones"] if resultado else 0


# =========================================================
# ENTRADAS VENDIDAS POR FRANJA HORARIA
# =========================================================

def obtener_entradas_vendidas_por_franja(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT

            CONCAT(
                LPAD(HOUR(f.fecha_hora_inicio), 2, '0'),
                ':00'
            ) AS franja,

            COUNT(e.id_entrada) AS cantidad

        FROM entradas AS e

        INNER JOIN compras AS c
            ON e.id_compra = c.id_compra

        INNER JOIN funciones AS f
            ON e.id_funcion = f.id_funcion

        WHERE c.estado = 'confirmada'
            AND e.estado IN ('confirmada', 'utilizada')
            AND c.fecha_confirmacion >= %s
            AND c.fecha_confirmacion <= NOW()

        GROUP BY
            CONCAT(
                LPAD(HOUR(f.fecha_hora_inicio), 2, '0'),
                ':00'
            )

        ORDER BY franja ASC;
    """

    return ejecutar_consulta(consulta, (fecha_desde,))


# =========================================================
# OCUPACIÓN POR FUNCIÓN
# =========================================================

def obtener_ocupacion_por_funcion(id_funcion=None, periodo=30):
    _marcar_funciones_finalizadas()

    fecha_desde = obtener_fecha_inicio(periodo)

    filtro = ""
    parametros = [fecha_desde]

    if id_funcion is not None:
        filtro = "AND f.id_funcion = %s"
        parametros.append(id_funcion)

    consulta = f"""
        SELECT

            f.id_funcion,

            p.nombre AS pelicula,

            f.id_sala,

            TIME_FORMAT(
                f.fecha_hora_inicio, '%H:%i'
            ) AS hora,

            s.capacidad AS capacidad_total,

            COUNT(c.id_compra) AS entradas_ocupadas,

            COALESCE(
                ROUND(
                    COUNT(c.id_compra) * 100.0 /
                    NULLIF(s.capacidad, 0),
                    2
                ),
                0
            ) AS porcentaje

        FROM funciones AS f

        INNER JOIN peliculas AS p
            ON f.id_pelicula = p.id_pelicula

        INNER JOIN salas AS s
            ON f.id_sala = s.id_sala

        LEFT JOIN entradas AS e
            ON f.id_funcion = e.id_funcion
            AND e.estado IN ('confirmada', 'utilizada')

        LEFT JOIN compras AS c
            ON e.id_compra = c.id_compra
            AND c.estado = 'confirmada'

        WHERE f.estado = 'finalizada'
            AND f.fecha_hora_inicio >= %s
            AND f.fecha_hora_inicio <= NOW()
            {filtro}

        GROUP BY
            f.id_funcion,
            p.nombre,
            f.id_sala,
            f.fecha_hora_inicio,
            s.capacidad

        ORDER BY f.fecha_hora_inicio DESC;
    """

    return ejecutar_consulta(consulta, tuple(parametros))


# =========================================================
# OCUPACIÓN POR PELÍCULA
# =========================================================

def obtener_ocupacion_por_pelicula(id_pelicula=None, periodo=30):
    _marcar_funciones_finalizadas()

    fecha_desde = obtener_fecha_inicio(periodo)

    filtro = ""
    parametros = [fecha_desde]

    if id_pelicula is not None:
        filtro = "AND f.id_pelicula = %s"
        parametros.append(id_pelicula)

    consulta = f"""
        SELECT

            p.id_pelicula,

            p.nombre AS pelicula,

            COUNT(*) AS cantidad_funciones,

            SUM(ocupacion.capacidad_total) AS capacidad_total,

            SUM(ocupacion.entradas_ocupadas) AS entradas_ocupadas,

            COALESCE(
                ROUND(
                    SUM(ocupacion.entradas_ocupadas) * 100.0 /
                    NULLIF(SUM(ocupacion.capacidad_total), 0),
                    2
                ),
                0
            ) AS porcentaje

        FROM (

            SELECT

                f.id_funcion,

                f.id_pelicula,

                s.capacidad AS capacidad_total,

                COUNT(c.id_compra) AS entradas_ocupadas

            FROM funciones AS f

            INNER JOIN salas AS s
                ON f.id_sala = s.id_sala

            LEFT JOIN entradas AS e
                ON f.id_funcion = e.id_funcion
                AND e.estado IN ('confirmada', 'utilizada')

            LEFT JOIN compras AS c
                ON e.id_compra = c.id_compra
                AND c.estado = 'confirmada'

            WHERE f.estado = 'finalizada'
                AND f.fecha_hora_inicio >= %s
                AND f.fecha_hora_inicio <= NOW()
                {filtro}

            GROUP BY
                f.id_funcion,
                f.id_pelicula,
                s.capacidad

        ) AS ocupacion

        INNER JOIN peliculas AS p
            ON ocupacion.id_pelicula = p.id_pelicula

        GROUP BY
            p.id_pelicula,
            p.nombre

        ORDER BY porcentaje DESC;
    """

    return ejecutar_consulta(consulta, tuple(parametros))