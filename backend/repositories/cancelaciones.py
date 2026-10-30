from db import ejecutar_consulta, ejecutar_transaccion


def obtener_compra_para_cancelar(id_compra: int) -> dict | None:
    """Consulta la compra junto con la fecha/hora de su función."""
    sql = """
        SELECT c.id_compra, c.estado, c.total, f.fecha_hora
        FROM compras c
        JOIN funciones f ON c.id_funcion = f.id_funcion
        WHERE c.id_compra = %s
    """
    resultados = ejecutar_consulta(sql, (id_compra,))
    return resultados[0] if resultados else None


def ejecutar_cancelacion_bd(id_compra: int, monto_reembolso: float) -> None:
    """Ejecuta la cancelación de la compra y sus entradas en una sola transacción."""
    sql_compra = """
        UPDATE compras
        SET estado = 'cancelada',
            fecha_cancelacion = NOW(),
            motivo_cancelacion = 'cliente',
            monto_reembolsado = %s
        WHERE id_compra = %s
    """
    sql_entradas = """
        UPDATE entradas
        SET estado = 'cancelada'
        WHERE id_compra = %s
    """
    consultas = [
        (sql_compra, (monto_reembolso, id_compra)),
        (sql_entradas, (id_compra,))
    ]

    ejecutar_transaccion(consultas)