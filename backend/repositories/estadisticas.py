from db import ejecutar_consulta
from datetime import datetime, timedelta


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



def obtener_ventas_totales(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COALESCE(SUM(total), 0) AS ventas_totales

        FROM compras

        WHERE estado = 'confirmada'
            AND fecha_confirmacion >= %s
            AND fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_totales"] if resultado else 0


def obtener_ventas_entradas(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COUNT(*) AS ventas_entradas

        FROM compras compra

        INNER JOIN entradas entrada
            ON compra.id_compra = entrada.id_compra

        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
            AND compra.fecha_confirmacion >= %s
            AND compra.fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_entradas"] if resultado else 0

def obtener_ventas_productos(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COALESCE(
                SUM(
                    compra_producto.cantidad *
                    compra_producto.precio_unitario
                ),
                0
            ) AS ventas_productos

        FROM compras compra

        INNER JOIN compra_productos compra_producto
            ON compra.id_compra = compra_producto.id_compra

        WHERE compra.estado = 'confirmada'
            AND compra.fecha_confirmacion >= %s
            AND compra.fecha_confirmacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["ventas_productos"] if resultado else 0


def obtener_ventas_por_genero(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            genero.nombre AS genero,

            COUNT(*) AS cantidad,

            SUM(entrada.precio_unitario) AS ventas_por_genero

        FROM compras compra

        INNER JOIN entradas entrada
            ON compra.id_compra = entrada.id_compra

        INNER JOIN funciones funcion
            ON entrada.id_funcion = funcion.id_funcion

        INNER JOIN peliculas pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        INNER JOIN pelicula_genero
            ON pelicula.id_pelicula = pelicula_genero.id_pelicula

        INNER JOIN generos genero
            ON pelicula_genero.id_genero = genero.id_genero

        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
            AND compra.fecha_confirmacion >= %s
            AND compra.fecha_confirmacion <= NOW()

        GROUP BY genero.id_genero, genero.nombre

        ORDER BY cantidad DESC;
    """

    return ejecutar_consulta(consulta, (fecha_desde,))

def obtener_cancelaciones(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT
            COUNT(*) AS cancelaciones

        FROM compras

        WHERE estado = 'cancelada'
            AND fecha_cancelacion IS NOT NULL
            AND fecha_cancelacion >= %s
            AND fecha_cancelacion <= NOW();
    """

    resultado = ejecutar_consulta(consulta, (fecha_desde,))

    return resultado[0]["cancelaciones"] if resultado else 0

def obtener_entradas_vendidas_por_franja(periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    consulta = """
        SELECT

            CONCAT(
                LPAD(HOUR(funcion.fecha_hora_inicio), 2, '0'),
                ':00'
            ) AS franja,

            COUNT(*) AS cantidad

        FROM entradas entrada

        INNER JOIN compras compra
            ON entrada.id_compra = compra.id_compra

        INNER JOIN funciones funcion
            ON entrada.id_funcion = funcion.id_funcion

        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
            AND compra.fecha_confirmacion >= %s
            AND compra.fecha_confirmacion <= NOW()

        GROUP BY HOUR(funcion.fecha_hora_inicio)

        ORDER BY cantidad DESC;
    """

    return ejecutar_consulta(consulta, (fecha_desde,))



def obtener_ocupacion_por_funcion(id_funcion=None, periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    filtro = ""
    parametros = [fecha_desde]

    if id_funcion is not None:
        filtro = "AND funcion.id_funcion = %s"
        parametros.append(id_funcion)

    consulta = f"""
        SELECT
            funcion.id_funcion,
            pelicula.nombre AS pelicula,
            funcion.id_sala,

            TIME_FORMAT(
                funcion.fecha_hora_inicio, '%H:%i'
            ) AS hora,

            COALESCE(capacidad.capacidad_total, 0) AS capacidad_total,

            COALESCE(ocupacion.entradas_ocupadas, 0) AS entradas_ocupadas,

            COALESCE(
                ROUND(
                    ocupacion.entradas_ocupadas * 100.0 /
                    NULLIF(capacidad.capacidad_total, 0),
                    2
                ),
                0
            ) AS porcentaje

        FROM funciones funcion

        INNER JOIN peliculas pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        LEFT JOIN (
            SELECT
                id_sala,
                COUNT(*) AS capacidad_total
            FROM butacas
            WHERE activa = TRUE
            GROUP BY id_sala
        ) capacidad
            ON funcion.id_sala = capacidad.id_sala

        LEFT JOIN (
            SELECT
                entrada.id_funcion,
                COUNT(*) AS entradas_ocupadas
            FROM entradas entrada
            INNER JOIN compras compra
                ON entrada.id_compra = compra.id_compra
            WHERE compra.estado = 'confirmada'
                AND entrada.estado IN ('confirmada', 'utilizada')
            GROUP BY entrada.id_funcion
        ) ocupacion
            ON funcion.id_funcion = ocupacion.id_funcion

        WHERE funcion.estado = 'finalizada'
            AND funcion.fecha_hora_inicio >= %s
            AND funcion.fecha_hora_inicio <= NOW()
            {filtro}

        ORDER BY funcion.fecha_hora_inicio DESC;
    """

    return ejecutar_consulta(consulta, tuple(parametros))

def obtener_ocupacion_por_pelicula(id_pelicula=None, periodo=30):

    fecha_desde = obtener_fecha_inicio(periodo)

    filtro = ""
    parametros = [fecha_desde]

    if id_pelicula is not None:
        filtro = "AND pelicula.id_pelicula = %s"
        parametros.append(id_pelicula)

    consulta = f"""
        SELECT
            pelicula.id_pelicula,
            pelicula.nombre AS pelicula,

            COUNT(funcion.id_funcion) AS cantidad_funciones,

            SUM(COALESCE(capacidad.capacidad_total, 0))
                AS capacidad_total,

            SUM(COALESCE(ocupacion.entradas_ocupadas, 0))
                AS entradas_ocupadas,

            COALESCE(
                ROUND(
                    SUM(COALESCE(ocupacion.entradas_ocupadas, 0)) * 100.0 /
                    NULLIF(
                        SUM(COALESCE(capacidad.capacidad_total, 0)),
                        0
                    ),
                    2
                ),
                0
            ) AS porcentaje

        FROM funciones funcion

        INNER JOIN peliculas pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        LEFT JOIN (
            SELECT
                id_sala,
                COUNT(*) AS capacidad_total
            FROM butacas
            WHERE activa = TRUE
            GROUP BY id_sala
        ) capacidad
            ON funcion.id_sala = capacidad.id_sala

        LEFT JOIN (
            SELECT
                entrada.id_funcion,
                COUNT(*) AS entradas_ocupadas
            FROM entradas entrada
            INNER JOIN compras compra
                ON entrada.id_compra = compra.id_compra
            WHERE compra.estado = 'confirmada'
                AND entrada.estado IN ('confirmada', 'utilizada')
            GROUP BY entrada.id_funcion
        ) ocupacion
            ON funcion.id_funcion = ocupacion.id_funcion

        WHERE funcion.estado = 'finalizada'
            AND funcion.fecha_hora_inicio >= %s
            AND funcion.fecha_hora_inicio <= NOW()
            {filtro}

        GROUP BY
            pelicula.id_pelicula,
            pelicula.nombre

        ORDER BY porcentaje DESC;
    """

    return ejecutar_consulta(consulta, tuple(parametros))