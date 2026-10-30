from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)

def listar_salas_por_local(id_local = None)->list[dict]:
    sql = 'SELECT s.* , l.nombre AS nombre_local FROM salas' \
    'INNER JOIN locales l ON l.id_local = s.id_local'
    parametros = ()
    if id_local is not None:
        sql += "WHERE s.id_local = %s"
        parametros = (id_local, )
    sql += "ORDER BY s.id_local, s.numero_sala"
    return ejecutar_consulta(sql, parametros)

def listar_sala_por_id(id_sala: int)-> dict:
    sql = 'SELECT * FROM salas WHERE id_sala = %s'
    filas = ejecutar_consulta(sql, (id_sala,))
    return filas[0] if filas else None

