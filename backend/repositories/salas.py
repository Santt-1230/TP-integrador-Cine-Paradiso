from db import (
    ejecutar_consulta,
    ejecutar_mutacion,
    transaccion
)
import constants as const

def obtener_butacas_a_quitar(cursor, id_sala, cantidad):
    sql = 'SELECT id_butaca FROM butacas WHERE id_sala = %s AND estado = %s' \
    ' ORDER BY fila DESC, numero DESC LIMIT %s FOR UPDATE'
    cursor.execute(sql, (id_sala, 'activa', cantidad))
    butacas = cursor.fetchall()
    ids_butacas = [butaca['id_butaca'] for butaca in butacas]
    if len(ids_butacas) != cantidad:
        raise RuntimeError('La cantidad de butacas activas no coincide con la capacidad')

    return ids_butacas

def validar_disponibilidad_futura(cursor, ids_butacas):
    valores = ', '.join(['%s'] * len(ids_butacas))

    sql = "SELECT COUNT(*) AS cantidad FROM entradas e JOIN funciones f ON f.id_funcion = e.id_funcion " \
    f'WHERE e.id_butaca IN ({valores})' "AND f.fecha_hora_inicio > NOW()" \
    " AND f.estado = 'programada' AND e.estado IN ('reservada', 'confirmada')"
    cursor.execute(sql, tuple(ids_butacas))

    return cursor.fetchone()['cantidad'] > 0

def desactivar_butacas(cursor, ids_butacas):
    valores = ', '.join(['%s'] * len(ids_butacas))
    sql = 'UPDATE butacas SET estado = %s' f'WHERE id_butaca IN ({valores})'
    parametros = ['inactiva']
    for id_butaca in ids_butacas:
        parametros.append(id_butaca)
    cursor.execute(sql, parametros)

def cambiar_estado_butacas(cursor, ids_butacas, estado):
    valores = ', '.join(['%s'] * len(ids_butacas))
    sql = 'UPDATE butacas SET estado = %s' f'WHERE id_butaca IN ({valores})'
    parametros = [estado]
    for id_butaca in ids_butacas:
        parametros.append(id_butaca)

    cursor.execute(sql, tuple(parametros))

def armar_asientos(filas):
    asientos = set()
    for item in filas:
        for numero in range(1, item['capacidad'] + 1):
            asientos.add((item['fila'],numero))
    return asientos

def sincronizar_butacas(cursor, id_sala, filas):
    deseados = armar_asientos(filas)
    sql = 'SELECT id_butaca, fila, numero, estado FROM butacas WHERE id_sala = %s FOR UPDATE'

    cursor.execute(sql, (id_sala,))
    existentes = {}
    for butaca in cursor.fetchall():
        existentes[(butaca['fila'], butaca['numero'])] = butaca

    a_desactivar = []
    a_reactivar = []
    a_crear = []

    for asiento, butaca in existentes.items():
        if asiento not in deseados and butaca['estado'] == 'activa':
            a_desactivar.append(butaca['id_butaca'])
        if asiento in deseados and butaca['estado'] == 'inactiva':
            a_reactivar.append(butaca['id_butaca'])

    for asiento in deseados:
        if asiento not in existentes:
            a_crear.append(asiento)

    if a_desactivar and validar_disponibilidad_futura(cursor, a_desactivar):
        return False

    if a_desactivar:
        cambiar_estado_butacas(cursor, a_desactivar, 'inactiva')
    if a_reactivar:
        cambiar_estado_butacas(cursor, a_reactivar, 'activa')

    sql = 'INSERT INTO butacas (id_sala, fila, numero) VALUES (%s, %s, %s)'
    parametros = (id_sala, fila, numero)

    for fila, numero in sorted(a_crear):
        cursor.execute(sql, parametros)

    return True



def reactivar_butacas(cursor, id_sala, cantidad):
    sql = 'SELECT id_butaca FROM butacas WHERE id_sala = %s' \
    ' AND estado = %s ORDER BY fila, numero LIMIT %s FOR UPDATE'
    cursor.execute(sql, (id_sala, 'inactiva', cantidad))

    butacas = cursor.fetchall()
    ids_butacas = [butaca['id_butaca'] for butaca in butacas]

    if ids_butacas:
        valores = ', '.join(['%s'] * len(ids_butacas))
        sql = 'UPDATE butacas SET estado = %s ' f'WHERE id_butaca IN ({valores})'
        parametros = ['activa']
        for id_butaca in ids_butacas:
            parametros.append(id_butaca)

        cursor.execute(sql, tuple(parametros))
    return len(ids_butacas)

def existe_sala_crear(id_local, numero_sala):
    sql = 'SELECT id_sala FROM salas WHERE id_local = %s AND numero_sala = %s'
    parametros = (id_local, numero_sala)
    return bool(ejecutar_consulta(sql, parametros))

def existe_sala_editar(id_local, numero_sala, id_sala):
    sql = 'SELECT id_sala FROM salas WHERE id_local = %s AND numero_sala =%s AND id_sala != %s'
    parametros = (id_local, numero_sala, id_sala)
    return bool(ejecutar_consulta(sql, parametros))

def listar_salas_por_local(id_local = None, estado = None)->list[dict]:
    sql = 'SELECT s.* , l.nombre AS nombre_local FROM salas s ' \
    'INNER JOIN locales l ON l.id_local = s.id_local'
    condiciones = []
    parametros = []


    if id_local is not None:
        condiciones.append('s.id_local = %s')
        parametros.append(id_local)
    if estado is not None:
        condiciones.append('s.estado = %s')
        parametros.append(estado)
    
    if condiciones:
        sql += ' WHERE ' + ' AND '.join(condiciones)
    sql += ' ORDER BY s.id_local, s.numero_sala'
    return ejecutar_consulta(sql, tuple(parametros))

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
    

def insertar_butacas(id_sala:int, capacidad:int, cursor = None, inicio = 0):
    valores = []
    parametros = []
    for i in range(inicio, inicio + capacidad):
        fila = chr(ord('A') + i // const.BUTACAS_POR_FILA)
        numero = i % const.BUTACAS_POR_FILA + 1
        valores.append('(%s, %s, %s)')
        parametros.extend((id_sala, fila, numero))

    sql = 'INSERT INTO butacas (id_sala, fila, numero) VALUES '+ ', '.join(valores)
    if cursor is not None:
        cursor.execute(sql, tuple(parametros))
    else:
        ejecutar_mutacion(sql, tuple(parametros))
    

def crear_sala_con_butacas(id_local, numero_sala, capacidad):
    id_sala = crear_sala(id_local, numero_sala, capacidad)
    insertar_butacas(id_sala, capacidad)
    return id_sala

def obtener_butacas(id_sala:int) -> list[dict]:
    sql = 'SELECT id_butaca, fila, numero FROM butacas ' \
    'WHERE id_sala = %s ORDER BY fila, numero'
    return ejecutar_consulta(sql, (id_sala,))

    
def actualizar_sala(id_sala, cambios):
    with transaccion() as cursor:
        if 'filas' in cambios:
            filas = cambios.pop('filas')
            if not sincronizar_butacas(cursor, id_sala, filas):
                return None
            cambios['capacidad'] = sum(item['cantidad'] for item in filas)

        campos = []
        parametros = []
        for campo, valor in cambios.items():
            campos.append(f"{campo} = %s")
            parametros.append(valor)
        parametros.append(id_sala)
        sql = f"UPDATE salas SET {', '.join(campos)} WHERE id_sala = %s"
        cursor.execute(sql, tuple(parametros))
    return listar_sala_por_id(id_sala)

def desactivar_sala(id_sala):
    sql = 'UPDATE salas SET estado = %s WHERE id_sala = %s'
    parametros = ('inactiva', id_sala,)
    ejecutar_mutacion(sql, parametros)
    return listar_sala_por_id(id_sala)

def listar_salas_activas(id_local:int)->list[dict]:
    sql = "SELECT id_sala, numero_sala, capacidad FROM salas " \
    "WHERE id_local = %s AND estado = 'activa' ORDER BY numero_sala"
    return ejecutar_consulta(sql, (id_local,))