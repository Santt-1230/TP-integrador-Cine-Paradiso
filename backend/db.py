import logging
import os
import mysql.connector

logger = logging.getLogger(__name__)

def obtener_conexion():
    variables = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    faltantes = [variable for variable in variables if not os.getenv(variable)]
    if faltantes:
        mensaje = f"Faltan variables de entorno: {', '.join(faltantes)}"
        logger.error(mensaje)
        raise RuntimeError(mensaje)
    try:
        puerto = int(os.getenv("DB_PORT"))
    except ValueError as error:
        mensaje = "DB_PORT debe ser un numero entero"
        logger.error(mensaje)
        raise RuntimeError(mensaje) from error
    try:
        conexion=mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            charset="utf8mb4",
            connection_timeout=5,
        )
    except mysql.connector.Error as error:
        logger.exception("No se pudo conectar con MySQL")
        raise RuntimeError("No se pudo conectar con la base de datos") from error
    return conexion

def ejecutar_consulta(sql:str, parametros : tuple = ())->list[dict]:
    conexion=obtener_conexion()
    cursor=None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql,parametros)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
    
def ejecutar_mutacion(sql:str, parametros :tuple = ())-> dict:
    conexion=obtener_conexion()
    cursor=None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql,parametros)
        conexion.commit()
        return {"id": cursor.lastrowid, "filas": cursor.rowcount}
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

