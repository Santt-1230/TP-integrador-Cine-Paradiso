from db import ejecutar_consulta, ejecutar_mutacion


def obtener_compra_para_cancelar(id_compra: int, id_usuario: int) -> dict | None:
    sql = """
        SELECT c.id_compra, c.id_usuario, c.estado, c.total, f.fecha_hora_inicio
        FROM compras c
        JOIN funciones f ON c.id_funcion = f.id_funcion
        WHERE c.id_compra = %s AND c.id_usuario = %s
    """
    resultados = ejecutar_consulta(sql, (id_compra, id_usuario))
    return resultados[0] if resultados else None


def ejecutar_cancelacion_bd(id_compra: int, monto_reembolso: float):
    sql_compra = """
        UPDATE compras
        SET estado = 'cancelada',
            fecha_cancelacion = NOW(),
            monto_reembolsado = %s
        WHERE id_compra = %s
    """
    ejecutar_mutacion(sql_compra, (monto_reembolso, id_compra))

    sql_entradas = """
        UPDATE entradas
        SET estado = 'cancelada'
        WHERE id_compra = %s
    """
    ejecutar_mutacion(sql_entradas, (id_compra,))

    sql_qr = """
        UPDATE qr
        SET estado = 'cancelado'
        WHERE id_compra = %s AND estado = 'valido'
    """
    ejecutar_mutacion(sql_qr, (id_compra,))