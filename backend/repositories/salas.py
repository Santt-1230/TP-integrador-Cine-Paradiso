from db import (
    ejecutar_consulta,
    ejecutar_mutacion
)

def listar_salas()->list[dict]:
    sql = 'SELECT * FROM salas ORDER BY id_sala, id_local'
    return ejecutar_consulta(sql)


