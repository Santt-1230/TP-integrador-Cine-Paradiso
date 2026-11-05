from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)

def listar_locales_activos():
    sql='SELECT id_local, nombre, direccion, activo FROM locales' \
    ' WHERE activo = TRUE ORDER BY nombre'
    return ejecutar_consulta(sql)

def obtener_local_id(id_local):
    sql='SELECT * FROM locales WHERE id_local = %s'
    filas = ejecutar_consulta(sql, (id_local,))
    return filas[0] if filas else None


