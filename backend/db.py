import logging
import os
from contextlib import contextmanager
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

    opciones_ssl = {}
    ruta_ca = os.getenv("DB_SSL_CA")
    if ruta_ca:
        opciones_ssl = {
            'ssl_ca' : ruta_ca,
            'ssl_verify_cert' : True,
        }
    try:
        conexion=mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=puerto,
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            charset="utf8mb4",
            connection_timeout=15,
            **opciones_ssl,
        )
    except (ValueError, mysql.connector.Error) as error:
        logger.exception("No se pudo conectar con MySQL")
        raise RuntimeError("No se pudo conectar con la base de datos") from error
    return conexion

def ejecutar_consulta(sql: str, parametros: tuple = ())->list[dict]:
    conexion=obtener_conexion()
    cursor=None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql,parametros)
        return cursor.fetchall()
    except mysql.connector.Error:
        logger.exception("Error de MySQL al ejecutar consulta")
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
    
def ejecutar_mutacion(sql: str, parametros: tuple = ())-> dict:
    conexion=obtener_conexion()
    cursor=None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql,parametros)
        conexion.commit()
        return {'id': cursor.lastrowid, 'filas' : cursor.rowcount}
    except Exception:
        logger.exception("Error al ejecutar la mutacion en la base de datos")
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

@contextmanager
def transaccion():
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        yield cursor
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()