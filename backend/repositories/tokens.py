from db import ejecutar_consulta, ejecutar_mutacion


def crear_token(id_usuario, tipo, token_hash, minutos_validez):
    sql = """INSERT INTO tokens_usuario (id_usuario, tipo, token_hash, expira_en)
             VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE))"""
    ejecutar_mutacion(sql, (id_usuario, tipo, token_hash, minutos_validez))


def buscar_token_valido(token_hash, tipo):
    sql = """SELECT id_token, id_usuario FROM tokens_usuario
             WHERE token_hash = %s AND tipo = %s AND usado = FALSE AND expira_en > NOW()"""
    filas = ejecutar_consulta(sql, (token_hash, tipo))
    return filas[0] if filas else None


def marcar_usado(id_token):
    ejecutar_mutacion("UPDATE tokens_usuario SET usado = TRUE WHERE id_token = %s", (id_token,))


def invalidar_tokens(id_usuario, tipo):
    sql = "UPDATE tokens_usuario SET usado = TRUE WHERE id_usuario = %s AND tipo = %s AND usado = FALSE"
    ejecutar_mutacion(sql, (id_usuario, tipo))