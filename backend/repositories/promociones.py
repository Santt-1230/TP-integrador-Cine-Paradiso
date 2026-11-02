from db import ejecutar_consulta

def obtener_promociones() -> list[dict]:
    sql = "SELECT * FROM promociones"
    return ejecutar_consulta(sql)
