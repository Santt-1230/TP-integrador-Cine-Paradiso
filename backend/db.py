import os
import mysql.connector


def obtener_conexion():
    variables = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    faltantes = [variable for variable in variables if not os.getenv(variable)]
    if faltantes:
        raise ConnectionError(f"Faltan variables de conexion: {', '.join(faltantes)}")
    
    conexion=mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conexion

def ejecutar_consulta(sql:str, parametros:tuple = ())-> list[dict]:
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary = True)
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

