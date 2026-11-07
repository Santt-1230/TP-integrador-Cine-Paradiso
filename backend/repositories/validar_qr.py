from db import ejecutar_consulta, ejecutar_mutacion, obtener_conexion



def validar_qr(token: str, id_validador: int) -> dict:

    sql = """
        UPDATE qr
        SET
            estado = 'utilizado',
            fecha_uso = NOW(),
            id_validador = %s
        WHERE token = %s
        AND estado = 'valido';
    """

    return ejecutar_mutacion(sql, (id_validador, token))


def obtener_qr(token: str) -> dict | None:

    sql = """
        SELECT
            id_qr,
            id_compra,
            id_entrada,
            tipo,
            estado,
            fecha_uso
        FROM qr
        WHERE token = %s;
    """

    resultado = ejecutar_consulta(sql, (token,))

    if not resultado:
        return None

    return resultado[0]