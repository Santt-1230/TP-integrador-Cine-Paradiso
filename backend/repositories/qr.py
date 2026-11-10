from db import ejecutar_consulta, ejecutar_mutacion
from mysql.connector import IntegrityError

def obtener_qr_de_entrada(id_entrada):
    sql =  "SELECT id_qr, tipo, token, codigo_manual, estado FROM qr WHERE id_entrada = %s AND estado <> 'cancelado'"
    parametros = [id_entrada]
    filas = ejecutar_consulta(sql, parametros)
    return filas[0] if filas else None

def registrar_qr(id_compra, id_entrada, tipo, token, codigo_manual):
    try:
        sql = "INSERT INTO qr (id_compra, id_entrada, tipo, token, codigo_manual) VALUES (%s, %s, %s, %s, %s)"
        parametros = [id_compra, id_entrada, tipo, token, codigo_manual]      
        ejecutar_mutacion(sql, parametros)
        return True
    except IntegrityError: # False cuando no se cumple con las reglas de la base de datos, UNIQUE..
        return False