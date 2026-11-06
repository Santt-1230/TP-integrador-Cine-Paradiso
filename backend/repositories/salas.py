from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)
import constants as const

def existe_sala(id_local, numero_sala):
    sql = 'SELECT id_sala FROM salas WHERE id_local = %s AND numero_sala = %s'
    return bool(ejecutar_consulta(sql, (id_local, numero_sala,)))

def listar_salas_por_local(id_local = None)->list[dict]:
    sql = 'SELECT s.* , l.nombre AS nombre_local FROM salas s ' \
    'INNER JOIN locales l ON l.id_local = s.id_local'
    parametros = ()
    if id_local is not None:
        sql += " WHERE s.id_local = %s"
        parametros = (id_local, )
    sql += " ORDER BY s.id_local, s.numero_sala"
    return ejecutar_consulta(sql, parametros)

def listar_sala_por_id(id_sala: int)-> dict | None:
    sql = 'SELECT * FROM salas WHERE id_sala = %s'
    filas = ejecutar_consulta(sql, (id_sala,))
    return filas[0] if filas else None

def crear_sala(id_local:int, numero_sala:int, capacidad:int):
    sql = 'INSERT INTO salas(id_local, numero_sala, capacidad) '\
    'VALUES (%s, %s, %s)'
    parametros = (id_local, numero_sala, capacidad)
    resultado = ejecutar_mutacion(sql, parametros)
    return resultado['id']
    

def insertar_butacas(id_sala:int, capacidad:int):
    sql = 'INSERT INTO butacas (id_sala, fila, numero)'\
    ' VALUES (%s, %s, %s)'
    for i in range(capacidad):
        fila= chr(ord('A') + i // const.BUTACAS_POR_FILA)
        numero = i % const.BUTACAS_POR_FILA + 1
        parametros = (id_sala, fila, numero)
        ejecutar_mutacion(sql, parametros)

def crear_sala_con_butacas(id_local, numero_sala, capacidad):
    id_sala = crear_sala(id_local, numero_sala, capacidad)
    insertar_butacas(id_sala, capacidad)
    return id_sala

def obtener_butacas(id_sala:int) -> list[dict]:
    sql = 'SELECT id_butaca, fila, numero FROM butacas ' \
    'WHERE id_sala = %s ORDER BY fila, numero'
    return ejecutar_consulta(sql, (id_sala,))

def actualizar_sala(id_sala, cambios):
    campos = []
    parametros = []
    for campo, valor in cambios.items():
        campos.append(f"{campo} = %s")
        parametros.append(valor)
    parametros.append(id_sala)
    sql = f"UPDATE salas SET {', '.join(campos)} WHERE id_sala = %s"
    ejecutar_mutacion(sql, tuple(parametros))
    return listar_sala_por_id(id_sala)

def desactivar_sala(id_sala):
    sql = 'UPDATE salas SET estado = %s WHERE id_sala = %s'
    parametros = ('inactiva', id_sala,)
    ejecutar_mutacion(sql, parametros)
    return listar_sala_por_id(id_sala)

def listar_salas_activas(id_local:int)->list[dict]:
    sql = "SELECT id_sala, numero_sala, capacidad FROM salas' \
    'WHERE id_local = %s AND estado = 'activa' ORDER BY numero_sala"
    parametros = (id_local,)
    return ejecutar_consulta(sql, parametros)