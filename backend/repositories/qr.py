from db import ejecutar_consulta, ejecutar_mutacion
from mysql.connector import IntegrityError

def obtener_qr_de_entrada(id_entrada):
    sql =  "SELECT id_qr, tipo, token, codigo_manual, estado FROM qr WHERE id_entrada = %s AND estado <> 'cancelado'"
    parametros = [id_entrada]
    filas = ejecutar_consulta(sql, parametros)
    return filas[0] if filas else None

def registrar_qr(id_compra, id_entrada, tipo, token, codigo_manual):
    try:
        sql = "INSERT INTO qr (id_compra, id_entrada, tipo, token, codigo_manual) VALUES (%s, %s, %s, %s, %s)"
        parametros = [id_compra, id_entrada, tipo, token, codigo_manual]      
        ejecutar_mutacion(sql, parametros)
        return True
    except IntegrityError: # False cuando no se cumple con las reglas de la base de datos, UNIQUE..
        return False

def registrar_qr_producto(cursor, id_compra, id_compra_producto, token, codigo_manual):
    try:
        sql = """
            INSERT INTO qr (id_compra, id_entrada, id_compra_producto, tipo, token, codigo_manual)
            VALUES (%s, NULL, %s, 'producto', %s, %s)
        """
        parametros = [id_compra, id_compra_producto,token,codigo_manual]
        cursor.execute(sql, parametros)
        return cursor.rowcount == 1
    except IntegrityError:
        return False

def obtener_qrs_productos_compra(id_compra):

    sql = """
        SELECT
            qr.id_qr,
            qr.id_compra,
            qr.id_compra_producto,
            qr.tipo,
            qr.token,
            qr.codigo_manual,
            qr.estado,

            compra_productos.id_producto,
            compra_productos.cantidad,
            compra_productos.precio_unitario,

            productos.nombre AS producto,
            productos.tipo AS categoria

        FROM qr

        INNER JOIN compra_productos
            ON qr.id_compra_producto =
               compra_productos.id_compra_producto

        INNER JOIN productos
            ON compra_productos.id_producto =
               productos.id_producto

        WHERE qr.id_compra = %s
        AND qr.tipo = 'producto'
        AND qr.estado <> 'cancelado'

        ORDER BY qr.id_qr
    """

    return ejecutar_consulta(sql, (id_compra,))