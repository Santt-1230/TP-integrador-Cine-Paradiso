from db import ejecutar_consulta, ejecutar_mutacion

def obtener_qr_entrada(token: str) -> dict | None:

    sql = """
        SELECT
            qr.id_qr,
            qr.id_compra,
            qr.id_entrada,
            qr.tipo,
            qr.estado AS estado_qr,
            qr.fecha_uso,

            entradas.estado AS estado_entrada,

            compras.estado AS estado_compra,
            compras.numero_factura,

            funciones.estado AS estado_funcion,

            peliculas.nombre AS pelicula,

            DATE_FORMAT(
                funciones.fecha_hora_inicio,
                '%d/%m/%Y'
            ) AS fecha,

            DATE_FORMAT(
                funciones.fecha_hora_inicio,
                '%H:%i'
            ) AS hora,

            salas.numero_sala AS sala,

            CONCAT(
                butacas.fila,
                butacas.numero
            ) AS butaca

        FROM qr

        INNER JOIN entradas
            ON qr.id_entrada = entradas.id_entrada
            AND qr.id_compra = entradas.id_compra

        INNER JOIN compras
            ON qr.id_compra = compras.id_compra
            AND entradas.id_funcion = compras.id_funcion

        INNER JOIN funciones
            ON entradas.id_funcion = funciones.id_funcion

        INNER JOIN peliculas
            ON funciones.id_pelicula = peliculas.id_pelicula

        INNER JOIN salas
            ON funciones.id_sala = salas.id_sala

        INNER JOIN butacas
            ON entradas.id_butaca = butacas.id_butaca

        WHERE qr.token = %s
        AND qr.tipo = 'entrada';
    """

    resultado = ejecutar_consulta(sql, (token,))

    if not resultado:
        return None

    return resultado[0]


def obtener_qr_producto(token: str) -> dict | None:

    sql = """
        SELECT
            qr.id_qr,
            qr.id_compra,
            qr.id_compra_producto,
            qr.tipo,
            qr.estado AS estado_qr,
            qr.fecha_uso,

            compras.estado AS estado_compra,
            compras.numero_factura,

            compra_productos.id_producto,
            compra_productos.cantidad,
            compra_productos.precio_unitario,

            productos.nombre AS producto,
            productos.tipo AS categoria,

            (
                compra_productos.cantidad *
                compra_productos.precio_unitario
            ) AS subtotal

        FROM qr

        INNER JOIN compra_productos
            ON qr.id_compra_producto =
               compra_productos.id_compra_producto

            AND qr.id_compra = compra_productos.id_compra

        INNER JOIN productos
            ON compra_productos.id_producto =
               productos.id_producto

        INNER JOIN compras
            ON qr.id_compra = compras.id_compra

        WHERE qr.token = %s
        AND qr.tipo = 'producto';
    """

    resultado = ejecutar_consulta(sql, (token,))

    if not resultado:
        return None

    return resultado[0]


def validar_qr_entrada(token: str, id_validador: int) -> dict:

    sql = """
        UPDATE qr

        INNER JOIN entradas
            ON qr.id_entrada = entradas.id_entrada
            AND qr.id_compra = entradas.id_compra

        INNER JOIN compras
            ON qr.id_compra = compras.id_compra
            AND entradas.id_funcion = compras.id_funcion

        INNER JOIN funciones
            ON entradas.id_funcion = funciones.id_funcion

        SET
            qr.estado = 'utilizado',
            qr.fecha_uso = NOW(),
            qr.id_validador = %s,

            entradas.estado = 'utilizada',
            entradas.fecha_uso = NOW()

        WHERE qr.token = %s

        AND qr.tipo = 'entrada'
        AND qr.estado = 'valido'

        AND entradas.estado = 'confirmada'
        AND compras.estado = 'confirmada'
        AND funciones.estado = 'programada';
    """

    return ejecutar_mutacion(sql, (id_validador, token))


def validar_qr_producto(
    token: str,
    id_validador: int,
    categoria: str
) -> dict:

    sql = """
        UPDATE qr

        INNER JOIN compra_productos
            ON qr.id_compra_producto =
               compra_productos.id_compra_producto

            AND qr.id_compra = compra_productos.id_compra

        INNER JOIN productos
            ON compra_productos.id_producto =
               productos.id_producto

        INNER JOIN compras
            ON qr.id_compra = compras.id_compra

        SET
            qr.estado = 'utilizado',
            qr.fecha_uso = NOW(),
            qr.id_validador = %s

        WHERE qr.token = %s

        AND qr.tipo = 'producto'
        AND qr.estado = 'valido'

        AND productos.tipo = %s
        AND compras.estado = 'confirmada';
    """

    return ejecutar_mutacion(
        sql,
        (id_validador, token, categoria)
    )