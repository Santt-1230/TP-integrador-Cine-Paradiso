"""Consultas SQL de peliculas, generos y pelicula_genero. No tiene reglas de negocio."""
from db import ejecutar_consulta, ejecutar_mutacion, transaccion

# "Vigente" = activa y dentro del periodo de cartelera. Las fechas son opcionales: NULL = sin limite.
VIGENTE = """
    p.activo = 1
    AND (p.cartelera_desde IS NULL OR p.cartelera_desde <= CURDATE())
    AND (p.cartelera_hasta IS NULL OR p.cartelera_hasta >= CURDATE())
"""
CAMPOS_PUBLICOS = """
    p.id_pelicula, p.nombre, p.sinopsis, p.poster_url, p.duracion_min,
    p.clasificacion, p.cartelera_desde, p.cartelera_hasta
"""


def generos_por_pelicula(ids):
    """{id_pelicula: [nombres de genero]} con una sola consulta."""
    if not ids:
        return {}
    marcas = ",".join(["%s"] * len(ids))
    filas = ejecutar_consulta(
        f"""SELECT pg.id_pelicula, g.nombre
            FROM pelicula_genero pg
            JOIN generos g ON g.id_genero = pg.id_genero
            WHERE pg.id_pelicula IN ({marcas})
            ORDER BY g.nombre""",
        tuple(ids),
    )
    resultado = {}
    for f in filas:
        resultado.setdefault(f["id_pelicula"], []).append(f["nombre"])
    return resultado


def listar_vigentes(genero=None, texto=None, limite=None):
    sql = f"SELECT {CAMPOS_PUBLICOS} FROM peliculas p WHERE {VIGENTE}"
    parametros = []
    if genero:
        sql += """ AND EXISTS (
                     SELECT 1 FROM pelicula_genero pg
                     JOIN generos g ON g.id_genero = pg.id_genero
                     WHERE pg.id_pelicula = p.id_pelicula AND g.nombre = %s)"""
        parametros.append(genero)
    if texto:
        sql += " AND p.nombre LIKE %s"
        parametros.append(f"%{texto}%")
    sql += " ORDER BY p.cartelera_desde DESC, p.nombre"
    if limite is not None:
        sql += " LIMIT %s"
        parametros.append(limite)
    return ejecutar_consulta(sql, tuple(parametros))


def buscar_activa(id_pelicula):
    filas = ejecutar_consulta(
        f"SELECT {CAMPOS_PUBLICOS} FROM peliculas p WHERE p.id_pelicula = %s AND p.activo = 1",
        (id_pelicula,),
    )
    return filas[0] if filas else None


def listar_admin(estado=None, texto=None):
    sql = """
        SELECT * FROM (
          SELECT p.id_pelicula, p.id_externo, p.nombre, p.sinopsis, p.poster_url,
                 p.duracion_min, p.clasificacion, p.cartelera_desde, p.cartelera_hasta, p.activo,
                 CASE
                   WHEN p.activo = 0 THEN 'inactiva'
                   WHEN p.cartelera_desde IS NOT NULL AND p.cartelera_desde > CURDATE() THEN 'proxima'
                   WHEN p.cartelera_hasta IS NOT NULL AND p.cartelera_hasta < CURDATE() THEN 'vencida'
                   ELSE 'vigente'
                 END AS estado_cartelera
          FROM peliculas p
        ) t
        WHERE 1 = 1
    """
    parametros = []
    if estado:
        sql += " AND t.estado_cartelera = %s"
        parametros.append(estado)
    if texto:
        sql += " AND t.nombre LIKE %s"
        parametros.append(f"%{texto}%")
    sql += " ORDER BY t.nombre"
    return ejecutar_consulta(sql, tuple(parametros))


def buscar_por_id(id_pelicula):
    """Fila completa (activa o no), o None."""
    filas = ejecutar_consulta(
        """SELECT id_pelicula, id_externo, nombre, sinopsis, poster_url, duracion_min,
                  clasificacion, cartelera_desde, cartelera_hasta, activo
           FROM peliculas WHERE id_pelicula = %s""",
        (id_pelicula,),
    )
    return filas[0] if filas else None


def buscar_id_por_externo(id_externo):
    filas = ejecutar_consulta("SELECT id_pelicula FROM peliculas WHERE id_externo = %s", (id_externo,))
    return filas[0]["id_pelicula"] if filas else None


def ids_externos_existentes(ids):
    if not ids:
        return set()
    marcas = ",".join(["%s"] * len(ids))
    filas = ejecutar_consulta(f"SELECT id_externo FROM peliculas WHERE id_externo IN ({marcas})", tuple(ids))
    return {f["id_externo"] for f in filas}


def obtener_periodo(id_pelicula):
    filas = ejecutar_consulta(
        "SELECT cartelera_desde, cartelera_hasta FROM peliculas WHERE id_pelicula = %s", (id_pelicula,))
    return filas[0] if filas else None


def obtener_activo(id_pelicula):
    """True/False segun `activo`, o None si no existe."""
    filas = ejecutar_consulta("SELECT activo FROM peliculas WHERE id_pelicula = %s", (id_pelicula,))
    return bool(filas[0]["activo"]) if filas else None


def dar_de_baja(id_pelicula):
    ejecutar_mutacion("UPDATE peliculas SET activo = 0 WHERE id_pelicula = %s", (id_pelicula,))


def crear_con_generos(id_externo, nombre, sinopsis, poster_url, duracion_min, clasificacion,
                      cartelera_desde, cartelera_hasta, activo, nombres_generos):
    """Inserta la pelicula y sus generos en una sola transaccion (los generos nuevos se crean)."""
    with transaccion() as cur:
        cur.execute(
            """INSERT INTO peliculas (id_externo, nombre, sinopsis, poster_url, duracion_min,
                                      clasificacion, cartelera_desde, cartelera_hasta, activo)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_externo, nombre, sinopsis, poster_url, duracion_min, clasificacion,
             cartelera_desde, cartelera_hasta, activo),
        )
        id_pelicula = cur.lastrowid
        for nombre_g in nombres_generos:
            cur.execute("INSERT IGNORE INTO generos (nombre) VALUES (%s)", (nombre_g,))
            cur.execute("SELECT id_genero FROM generos WHERE nombre = %s", (nombre_g,))
            id_genero = cur.fetchone()["id_genero"]
            cur.execute("INSERT IGNORE INTO pelicula_genero (id_pelicula, id_genero) VALUES (%s, %s)",
                        (id_pelicula, id_genero))
    return id_pelicula


def actualizar(id_pelicula, campos, nombres_generos=None):
    """Actualiza campos y/o reemplaza los generos en una sola transaccion.

    Devuelve la lista de generos inexistentes; si no esta vacia, no se escribio nada.
    `campos` solo trae columnas de una lista fija (validada), nunca texto del cliente.
    """
    with transaccion() as cur:
        ids_generos = None
        if nombres_generos is not None:
            ids_generos = []
            if nombres_generos:
                marcas = ",".join(["%s"] * len(nombres_generos))
                cur.execute(f"SELECT id_genero, nombre FROM generos WHERE nombre IN ({marcas})",
                            tuple(nombres_generos))
                encontrados = {r["nombre"].lower(): r["id_genero"] for r in cur.fetchall()}
                faltan = [n for n in nombres_generos if n.lower() not in encontrados]
                if faltan:
                    return faltan
                ids_generos = sorted(set(encontrados.values()))
        if campos:
            sets = ", ".join(f"{c} = %s" for c in campos)
            cur.execute(f"UPDATE peliculas SET {sets} WHERE id_pelicula = %s", (*campos.values(), id_pelicula))
        if ids_generos is not None:
            cur.execute("DELETE FROM pelicula_genero WHERE id_pelicula = %s", (id_pelicula,))
            if ids_generos:
                cur.executemany("INSERT INTO pelicula_genero (id_pelicula, id_genero) VALUES (%s, %s)",
                                [(id_pelicula, g) for g in ids_generos])
    return []
