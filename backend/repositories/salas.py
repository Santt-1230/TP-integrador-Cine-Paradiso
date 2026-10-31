from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)
import constants as const

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

def crear_sala(id_local:int, numero_sala:int, capacidad:int):
    sql = 'INSERT INTO salas(id_local, numero_sala, capacidad)' \
    'VALUES (%s, %s, %s)'
    resultado = ejecutar_mutacion(sql, (id_local, numero_sala, capacidad))
    return resultado['id']
    

def insertar_butacas(id_sala, capacidad):
    sql = 'INSERT INTO butacas (id_sala, fila, columna)' \
    'VALUES (%s, %s, %s)'
    for i in range(capacidad):
        fila= chr(ord('A') + i // const.BUTACAS_POR_FILA)
        columna = i % const.BUTACAS_POR_FILA + 1
        ejecutar_mutacion(sql, (id_sala, fila, columna))

def crear_sala_con_butacas(id_local, numero_sala, capacidad):
    id_sala = crear_sala(id_local, numero_sala, capacidad)
    insertar_butacas(id_sala, capacidad)
    return id_sala

