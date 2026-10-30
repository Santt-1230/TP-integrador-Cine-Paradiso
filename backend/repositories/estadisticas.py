from db import obtener_conexion


from db import obtener_conexion


def obtener_ventas_totales(periodo):

    agrupaciones = {
        "anual": "YEAR(fecha_confirmacion)",
        "mensual": "YEAR(fecha_confirmacion), MONTH(fecha_confirmacion)",
        "diario": "YEAR(fecha_confirmacion), MONTH(fecha_confirmacion), DAY(fecha_confirmacion)"
    }

    agrupacion = agrupaciones[periodo]

    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(f"""
            SELECT
                YEAR(fecha_confirmacion) AS anio,
                MONTH(fecha_confirmacion) AS mes,
                DAY(fecha_confirmacion) AS dia,
                SUM(total) AS ventas_totales
            FROM compras
            WHERE estado = 'confirmada'
            GROUP BY {agrupacion}
            ORDER BY anio, mes, dia;
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()
