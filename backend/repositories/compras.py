from db import ejecutar_consulta, ejecutar_mutacion
from mysql.connector import IntegrityError


def obtener_compras(id):
    sql = "SELECT * FROM compras WHERE id_usuario = %s;"
    params = [id]
    compras = ejecutar_consulta(sql, params)
    return compras


def obtener_compra_id(id_compra, id_usuario):
    sql = "SELECT * FROM compras WHERE id_compra = %s"
    parametros = [id_compra]
    if id_usuario is not None:
        sql += " AND id_usuario = %s"
        parametros.append(id_usuario)
    compra = ejecutar_consulta(sql, parametros)
    return  compra[0] if compra else None

#validar que la butaca este activa, o libre, y agregar datos a la base de butacas

def registrar_compra(id_usuario, datos):
    funcion = obtener_funcion(datos["id_funcion"])
    total_pagar = funcion["precio_entrada"] * int(len(datos["butacas"]))
    parametros = [id_usuario, datos["id_funcion"], total_pagar]
    sql = "INSERT INTO compras (id_usuario, id_funcion, total, expira_en) VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE) )"
    cambio_compras = ejecutar_mutacion(sql,parametros)

    id_compra = cambio_compras["id"]

    cambio_entradas = registrar_entrada(id_compra, datos, funcion["precio_entrada"])
    return cambio_compras["filas"] > 0 and cambio_entradas

def registrar_entrada(id_compra,datos, precio_unitario):
    total_cambios = 0
    for butaca in datos["butacas"]:
        sql = "INSERT INTO entradas (id_compra, id_funcion, id_butaca, precio_unitario) VALUES (%s, %s, %s, %s)"
        parametros = [id_compra, datos["id_funcion"], butaca, precio_unitario]
        resultado = ejecutar_mutacion(sql, parametros)
        if resultado["filas"] > 0:
            total_cambios += 1
    return total_cambios == len(datos["butacas"])

def butacas_disponibles(id_funcion, id_butacas):
    if not id_butacas:
        return False

    marcadores = ", ".join(["%s"] * len(id_butacas))
    sql = (
        "SELECT e.id_butaca "
        "FROM entradas e "
        "INNER JOIN compras c ON c.id_compra = e.id_compra "
        f"WHERE e.id_funcion = %s AND e.id_butaca IN ({marcadores}) "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW()))"
    )

    parametros = (id_funcion, *id_butacas)
    butacas_ocupadas = ejecutar_consulta(sql, parametros)
    return not butacas_ocupadas


def obtener_funcion_precio(id_funcion):
    sql = "SELECT precio_entrada from funciones WHERE id_funcion = %s"
    parametros = [id_funcion]
    precio_unitario = ejecutar_consulta(sql, parametros)
    return precio_unitario[0] if precio_unitario else None


def cancelacion_de_compra(id_compra, id_usuario):
    sql = "UPDATE compras SET estado = 'cancelada', fecha_cancelacion = NOW()  WHERE id_compra = %s AND id_usuario = %s AND (estado = 'confirmada' OR estado = 'pendiente')"
    parametros = [id_compra, id_usuario]
    print (parametros)
    cambiar = ejecutar_mutacion(sql, parametros)
    return cambiar["filas"] > 0

def obtener_entradas(id_compra):
    sql = "SELECT * FROM entradas WHERE id_compra = %s"
    parametros = [id_compra]
    entradas = ejecutar_consulta(sql, parametros)
    return entradas


def listar_entradas_confirmadas(id_compra):
    sql = "SELECT id_entrada FROM entradas WHERE id_compra = %s AND estado = 'confirmada'"
    parametros = [id_compra]
    return ejecutar_consulta(sql, parametros)

def obtener_funcion(id_funcion):
    sql = "SELECT * FROM funciones WHERE id_funcion = %s"
    parametros = [id_funcion]
    funcion = ejecutar_consulta(sql, parametros)
    return funcion[0] if funcion else None