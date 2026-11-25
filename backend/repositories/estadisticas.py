from db import ejecutar_consulta, ejecutar_mutacion
from services.estadisticas import obtener_fecha_inicio

def obtener_ventas_totales(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT COALESCE(SUM(total), 0) AS ventas_totales
        FROM compras
        WHERE estado = 'confirmada'
        AND fecha_confirmacion BETWEEN %s AND NOW()
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_totales"] if resultado else 0


def obtener_ventas_entradas(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT COUNT(entrada.id_entrada) AS ventas_entradas

        FROM compras AS compra

        INNER JOIN entradas AS entrada
            ON compra.id_compra = entrada.id_compra

        WHERE compra.estado = 'confirmada'
        AND entrada.estado IN ('confirmada', 'utilizada')
        AND compra.fecha_confirmacion BETWEEN %s AND NOW()
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_entradas"] if resultado else 0


def obtener_ventas_productos(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT COALESCE(
            SUM(producto.cantidad * producto.precio_unitario),
            0
        ) AS ventas_productos

        FROM compras AS compra

        INNER JOIN compra_productos AS producto
            ON compra.id_compra = producto.id_compra

        WHERE compra.estado = 'confirmada'
        AND compra.fecha_confirmacion BETWEEN %s AND NOW()
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_productos"] if resultado else 0

def obtener_ventas_por_genero(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            genero.nombre AS genero,
            COUNT(entrada.id_entrada) AS cantidad,
            SUM(entrada.precio_unitario) AS ventas_por_genero

        FROM compras AS compra

        INNER JOIN entradas AS entrada
            ON compra.id_compra = entrada.id_compra

        INNER JOIN funciones AS funcion
            ON entrada.id_funcion = funcion.id_funcion

        INNER JOIN peliculas AS pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        INNER JOIN pelicula_genero
            ON pelicula.id_pelicula = pelicula_genero.id_pelicula

        INNER JOIN generos AS genero
            ON pelicula_genero.id_genero = genero.id_genero

        WHERE compra.estado = 'confirmada'
        AND entrada.estado IN ('confirmada', 'utilizada')
        AND compra.fecha_confirmacion BETWEEN %s AND NOW()

        GROUP BY genero.id_genero, genero.nombre

        ORDER BY cantidad DESC
    """

    return ejecutar_consulta(consulta, (fecha_desde,))


def obtener_cancelaciones(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT COUNT(*) AS cancelaciones
        FROM compras
        WHERE estado = 'cancelada'
        AND fecha_cancelacion BETWEEN %s AND NOW()
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["cancelaciones"] if resultado else 0

def obtener_entradas_vendidas_por_franja(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            DATE_FORMAT(funcion.fecha_hora_inicio, '%H:00') AS franja,

            COUNT(entrada.id_entrada) AS cantidad

        FROM entradas AS entrada

        INNER JOIN compras AS compra
            ON entrada.id_compra = compra.id_compra

        INNER JOIN funciones AS funcion
            ON entrada.id_funcion = funcion.id_funcion

        WHERE compra.estado = 'confirmada'
        AND entrada.estado IN ('confirmada', 'utilizada')
        AND compra.fecha_confirmacion BETWEEN %s AND NOW()

        GROUP BY franja

        ORDER BY franja ASC
    """

    return ejecutar_consulta(consulta, (fecha_desde,))

def obtener_ocupacion_por_funcion(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            funcion.id_funcion,
            pelicula.nombre AS pelicula,
            funcion.id_sala,

            TIME_FORMAT(
                funcion.fecha_hora_inicio, '%H:%i'
            ) AS hora,

            sala.capacidad AS capacidad_total,

            COUNT(compra.id_compra) AS entradas_ocupadas,

            COALESCE(
                ROUND(
                    COUNT(compra.id_compra) * 100.0 /
                    NULLIF(sala.capacidad, 0),
                    2
                ),
                0
            ) AS porcentaje

        FROM funciones AS funcion

        INNER JOIN peliculas AS pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        INNER JOIN salas AS sala
            ON funcion.id_sala = sala.id_sala

        LEFT JOIN entradas AS entrada
            ON funcion.id_funcion = entrada.id_funcion
            AND entrada.estado IN ('confirmada', 'utilizada')

        LEFT JOIN compras AS compra
            ON entrada.id_compra = compra.id_compra
            AND compra.estado = 'confirmada'

        WHERE funcion.estado = 'finalizada'
        AND funcion.fecha_hora_inicio BETWEEN %s AND NOW()

        GROUP BY
            funcion.id_funcion,
            pelicula.nombre,
            funcion.id_sala,
            funcion.fecha_hora_inicio,
            sala.capacidad

        ORDER BY funcion.fecha_hora_inicio DESC
    """

    return ejecutar_consulta(consulta, (fecha_desde,))

def obtener_ocupacion_por_pelicula(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            pelicula.id_pelicula,
            pelicula.nombre AS pelicula,

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
                funcion.id_funcion,
                funcion.id_pelicula,

                sala.capacidad AS capacidad_total,

                COUNT(compra.id_compra) AS entradas_ocupadas

            FROM funciones AS funcion

            INNER JOIN salas AS sala
                ON funcion.id_sala = sala.id_sala

            LEFT JOIN entradas AS entrada
                ON funcion.id_funcion = entrada.id_funcion
                AND entrada.estado IN ('confirmada', 'utilizada')

            LEFT JOIN compras AS compra
                ON entrada.id_compra = compra.id_compra
                AND compra.estado = 'confirmada'

            WHERE funcion.estado = 'finalizada'
            AND funcion.fecha_hora_inicio >= %s
            AND funcion.fecha_hora_inicio <= NOW()

            GROUP BY
                funcion.id_funcion,
                funcion.id_pelicula,
                sala.capacidad

        ) AS ocupacion

        INNER JOIN peliculas AS pelicula
            ON ocupacion.id_pelicula = pelicula.id_pelicula

        GROUP BY
            pelicula.id_pelicula,
            pelicula.nombre

        ORDER BY porcentaje DESC
    """

    return ejecutar_consulta(consulta, (fecha_desde,))