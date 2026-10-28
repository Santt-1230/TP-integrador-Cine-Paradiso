import os
import mysql.connector


def obtener_conexion():
    variables = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
    faltantes = [variable for variable in variables if not os.getenv(variable)]
    if faltantes:
        raise ConnectionError(f"Faltan variables: {', '.join(faltantes)}")
    try:
        conexion = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = int(os.getenv("DB_PORT")),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD")
        )
    except mysql.connector.Error as e:
        raise ConnectionError("No se pudo conectar con la base de datos") from e
    
    return conexion

