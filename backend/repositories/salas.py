from db import (
    ejecutar_consulta,
    ejecutar_mutacion,
    transaccion
)

def listar_filas_sala(id_sala: int) -> list[dict]:
    sql = ("SELECT fila, COUNT(*) AS cantidad FROM butacas "
           "WHERE id_sala = %s AND estado = 'activa' GROUP BY fila ORDER BY fila")
    return ejecutar_consulta(sql, (id_sala,))

def validar_disponibilidad_futura(cursor, ids_butacas):
    valores = ', '.join(['%s'] * len(ids_butacas))

    sql = "SELECT COUNT(*) AS cantidad FROM entradas e JOIN funciones f ON f.id_funcion = e.id_funcion " \
    f'WHERE e.id_butaca IN ({valores})' " AND f.fecha_hora_inicio > NOW() " \
    " AND f.estado = 'programada' AND e.estado IN ('reservada', 'confirmada')"
    cursor.execute(sql, tuple(ids_butacas))

    return cursor.fetchone()['cantidad'] > 0

def cambiar_estado_butacas(cursor, ids_butacas, estado):
    valores = ', '.join(['%s'] * len(ids_butacas))
    sql = 'UPDATE butacas SET estado = %s ' f'WHERE id_butaca IN ({valores})'
    parametros = [estado]
    for id_butaca in ids_butacas:
        parametros.append(id_butaca)

    cursor.execute(sql, tuple(parametros))

def armar_asientos(filas):
    asientos = set()
    for item in filas:
        for numero in range(1, item['cantidad'] + 1):
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
    if a_crear:
        cursor.executemany(
            sql, [(id_sala, fila, numero) for fila, numero in sorted(a_crear)]
            )

    return True


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

def crear_sala(id_local, numero_sala, filas):
    capacidad = sum(item['cantidad'] for item in filas)

    with transaccion() as cursor:
        cursor.execute(
            'INSERT INTO salas (id_local, numero_sala, capacidad) '
            'VALUES (%s, %s, %s)',
            (id_local, numero_sala, capacidad)
        )
        id_sala = cursor.lastrowid
        sincronizar_butacas(cursor, id_sala, filas)

    return listar_sala_por_id(id_sala)

    
def actualizar_sala(id_sala, cambios):
    cambios = cambios.copy()
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
