from db import ejecutar_consulta_uno, obtener_conexion


def obtener_compra_para_cancelar(id_compra: int) -> dict | None:
    """Consulta la compra junto con la fecha/hora de la función asociada."""
    sql = """
        SELECT c.id_compra, c.estado, c.total, f.fecha_hora
        FROM compras c
        JOIN funciones f ON c.id_funcion = f.id_funcion
        WHERE c.id_compra = %s
    """
    return ejecutar_consulta_uno(sql, (id_compra,))


def ejecutar_cancelacion_bd(id_compra: int, monto_reembolso: float) -> None:
    """Actualiza de forma atómica los estados de la compra y sus entradas."""
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor()

        sql_compra = """
            UPDATE compras
            SET estado = 'cancelada',
                fecha_cancelacion = NOW(),
                motivo_cancelacion = 'cliente',
                monto_reembolsado = %s
            WHERE id_compra = %s
        """
        cursor.execute(sql_compra, (monto_reembolso, id_compra))

        sql_entradas = """
            UPDATE entradas
            SET estado = 'cancelada'
            WHERE id_compra = %s
        """
        cursor.execute(sql_entradas, (id_compra,))

        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()