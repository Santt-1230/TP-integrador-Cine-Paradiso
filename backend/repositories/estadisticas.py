from db import obtener_conexion


def obtener_ventas_totales():
    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""SELECT SUM(ventas) AS ventas_totales
FROM (
    SELECT SUM(precio) AS ventas
    FROM entrada

    UNION ALL

    SELECT SUM(precio) AS ventas
    FROM productos
) AS total;
            
            """)

    finally:
        cursor.close()
        conexion.close()
