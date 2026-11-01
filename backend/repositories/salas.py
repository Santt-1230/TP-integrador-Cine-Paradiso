from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)
import constants as const

def existe_sala(id_local, numero_sala):
    sql = 'SELECT id_sala FROM salas WHERE id_local = %s AND numero_sala = %s'
    return bool(ejecutar_consulta(sql, (id_local, numero_sala)))

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
    sql = 'INSERT INTO butacas (id_sala, fila, numero)' \
    'VALUES (%s, %s, %s)'
    for i in range(capacidad):
        fila= chr(ord('A') + i // const.BUTACAS_POR_FILA)
        numero = i % const.BUTACAS_POR_FILA + 1
        ejecutar_mutacion(sql, (id_sala, fila, numero))

def crear_sala_con_butacas(id_local, numero_sala, capacidad):
    id_sala = crear_sala(id_local, numero_sala, capacidad)
    insertar_butacas(id_sala, capacidad)
    return id_sala

def obtener_butacas(id_sala):
    sql = 'SELECT id_butaca, fila, numero, activa FROM butacas' \
    'WHERE id_sala = %s ORDER BY fila, numero'
    ejecutar_consulta(sql, (id_sala,))

def actualizar_sala(id_sala, cambios):
    campos = []
    parametros = []
    if 'numero_sala' in cambios:
        campos.append('numero_sala')
        parametros.append(cambios['numero_sala'])

    if 'estado' in cambios:
        campos.append('estado')
        parametros.append(cambios['estado'])

    parametros.append(id_sala)

    sql = "UPDATE salas SET {', '.join(campos)} WHERE id_sala = %s"
    ejecutar_mutacion(sql, tuple(parametros))
    return listar_sala_por_id(id_sala)

def desactivar_sala(id_sala):
    sql = 'UPDATE salas SET estado = %s WHERE id_sala = %s'
    ejecutar_mutacion(sql, ('inactiva', id_sala))
    return listar_sala_por_id(id_sala)