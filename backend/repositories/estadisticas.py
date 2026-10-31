from db import ejecutar_consulta


def obtener_ventas_totales(periodo):

    agrupaciones = {
        "anual": (
            "YEAR(fecha_confirmacion) AS anio",
            "YEAR(fecha_confirmacion)",
            "anio"
        ),
        "mensual": (
            "YEAR(fecha_confirmacion) AS anio, "
            "MONTH(fecha_confirmacion) AS mes",
            "YEAR(fecha_confirmacion), MONTH(fecha_confirmacion)",
            "anio, mes"
        ),
        "diario": (
            "YEAR(fecha_confirmacion) AS anio, "
            "MONTH(fecha_confirmacion) AS mes, "
            "DAY(fecha_confirmacion) AS dia",
            "YEAR(fecha_confirmacion), MONTH(fecha_confirmacion), "
            "DAY(fecha_confirmacion)",
            "anio, mes, dia"
        )
    }

    if periodo not in agrupaciones:
        raise ValueError("El período debe ser anual, mensual o diario")

    columnas, agrupacion, orden = agrupaciones[periodo]

    consulta = f"""
        SELECT
            {columnas},
            SUM(total) AS ventas_totales
        FROM compras
        WHERE estado = 'confirmada'
        GROUP BY {agrupacion}
        ORDER BY {orden};
    """

    return ejecutar_consulta(consulta)


def obtener_ventas_entradas():

    consulta = """
        SELECT
            YEAR(compra.fecha_confirmacion) AS anio,
            MONTH(compra.fecha_confirmacion) AS mes,
            DAY(compra.fecha_confirmacion) AS dia,
            SUM(entrada.precio_unitario) AS ventas_entradas
        FROM compras compra
        JOIN entradas entrada
            ON compra.id_compra = entrada.id_compra
        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
        GROUP BY anio, mes, dia
        ORDER BY anio, mes, dia;
    """

    return ejecutar_consulta(consulta)


def obtener_ventas_productos():

    consulta = """
        SELECT
            YEAR(compra.fecha_confirmacion) AS anio,
            MONTH(compra.fecha_confirmacion) AS mes,
            DAY(compra.fecha_confirmacion) AS dia,
            SUM(
                compra_producto.cantidad *
                compra_producto.precio_unitario
            ) AS ventas_servicios
        FROM compras compra
        JOIN compra_producto
            ON compra.id_compra = compra_producto.id_compra
        JOIN productos producto
            ON compra_producto.id_producto = producto.id_producto
        WHERE compra.estado = 'confirmada'
        GROUP BY anio, mes, dia
        ORDER BY anio, mes, dia;
    """

    return ejecutar_consulta(consulta)


def obtener_ventas_por_genero():

    consulta = """
        SELECT
            genero.nombre AS genero,
            SUM(entrada.precio_unitario) AS ventas_por_genero
        FROM compras compra
        JOIN entradas entrada
            ON compra.id_compra = entrada.id_compra
        JOIN funciones funcion
            ON entrada.id_funcion = funcion.id_funcion
        JOIN peliculas pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula
        JOIN pelicula_genero
            ON pelicula.id_pelicula = pelicula_genero.id_pelicula
        JOIN generos genero
            ON pelicula_genero.id_genero = genero.id_genero
        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
        GROUP BY genero.id_genero, genero.nombre
        ORDER BY ventas_por_genero DESC;
    """

    return ejecutar_consulta(consulta)


def obtener_cancelaciones():

    consulta = """
        SELECT
            YEAR(fecha_cancelacion) AS anio,
            MONTH(fecha_cancelacion) AS mes,
            DAY(fecha_cancelacion) AS dia,
            COUNT(*) AS cancelaciones
        FROM compras
        WHERE estado = 'cancelada'
            AND fecha_cancelacion IS NOT NULL
        GROUP BY anio, mes, dia
        ORDER BY anio, mes, dia;
    """

    return ejecutar_consulta(consulta)



def obtener_entradas_vendidas_por_franja():

    consulta = """
        SELECT
            HOUR(funcion.fecha_hora_inicio) AS franja_horaria,
            COUNT(DISTINCT entrada.id_entrada) AS entradas_vendidas
        FROM compras compra
        JOIN entradas entrada
            ON compra.id_compra = entrada.id_compra
        JOIN funciones funcion
            ON entrada.id_funcion = funcion.id_funcion
        WHERE compra.estado = 'confirmada'
            AND entrada.estado IN ('confirmada', 'utilizada')
        GROUP BY franja_horaria
        ORDER BY entradas_vendidas DESC;
    """

    return ejecutar_consulta(consulta)


def obtener_ocupacion_por_funcion():

    consulta = """
        SELECT
            funcion.id_funcion,
            pelicula.id_pelicula,
            pelicula.nombre AS pelicula,
            sala.id_sala,
            funcion.fecha_hora_inicio,

            COUNT(DISTINCT butaca.id_butaca) AS capacidad_total, 

            COUNT(DISTINCT entrada.id_butaca) AS espectadores,

            ROUND(
                COUNT(DISTINCT entrada.id_butaca) * 100.0 /
                NULLIF(COUNT(DISTINCT butaca.id_butaca), 0),
                2
            ) AS porcentaje_ocupacion

        FROM funciones funcion

        JOIN peliculas pelicula
            ON funcion.id_pelicula = pelicula.id_pelicula

        JOIN salas sala
            ON funcion.id_sala = sala.id_sala

        LEFT JOIN butacas butaca
            ON sala.id_sala = butaca.id_sala

        LEFT JOIN entradas entrada
            ON funcion.id_funcion = entrada.id_funcion
            AND entrada.id_butaca = butaca.id_butaca
            AND entrada.estado = 'utilizada'

        WHERE funcion.estado = 'finalizada'

        GROUP BY
            funcion.id_funcion,
            pelicula.id_pelicula,
            pelicula.nombre,
            sala.id_sala,
            funcion.fecha_hora_inicio

        ORDER BY funcion.fecha_hora_inicio DESC;
    """

    return ejecutar_consulta(consulta)


def obtener_ocupacion_por_pelicula():

    consulta = """
        SELECT
            pelicula.id_pelicula,
            pelicula.nombre AS pelicula,

            COUNT(ocupacion.id_funcion) AS cantidad_funciones,

            SUM(ocupacion.capacidad_total) AS capacidad_total,

            SUM(ocupacion.espectadores) AS espectadores,

            ROUND(
                SUM(ocupacion.espectadores) * 100.0 /
                NULLIF(SUM(ocupacion.capacidad_total), 0),
                2
            ) AS porcentaje_ocupacion

        FROM (
            SELECT
                funcion.id_funcion,
                funcion.id_pelicula,

                COUNT(DISTINCT butaca.id_butaca) AS capacidad_total,

                COUNT(DISTINCT entrada.id_butaca) AS espectadores

            FROM funciones funcion

            JOIN salas sala
                ON funcion.id_sala = sala.id_sala

            LEFT JOIN butacas butaca
                ON sala.id_sala = butaca.id_sala

            LEFT JOIN entradas entrada
                ON funcion.id_funcion = entrada.id_funcion
                AND entrada.id_butaca = butaca.id_butaca
                AND entrada.estado = 'utilizada'

            WHERE funcion.estado = 'finalizada'

            GROUP BY
                funcion.id_funcion,
                funcion.id_pelicula

        ) ocupacion

        JOIN peliculas pelicula
            ON ocupacion.id_pelicula = pelicula.id_pelicula

        GROUP BY
            pelicula.id_pelicula,
            pelicula.nombre

        ORDER BY porcentaje_ocupacion DESC;
    """

    return ejecutar_consulta(consulta)