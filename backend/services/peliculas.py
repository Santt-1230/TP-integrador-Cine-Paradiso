"""Reglas de peliculas y cartelera. Devuelven (resultado, error); el error es una tupla
(estado_http, code, message, description) que la ruta convierte con construir_error_api."""
import constants as const
import tmdb
from repositories import peliculas as repo
from validators import peliculas as validador
from validators.peliculas import FECHAS, a_fecha


def _con_estado(error, estado=400):
    return (estado, *error)


def _no_encontrada(id_pelicula, solo_activas=True):
    detalle = f"No existe la pelicula {id_pelicula}" + (" o no esta activa" if solo_activas else "")
    return (404, const.ERROR_CODE_NOT_FOUND, "Pelicula no encontrada", detalle)


def _serializar(fila, generos):
    for campo in FECHAS:
        if fila.get(campo) is not None:
            fila[campo] = fila[campo].isoformat()
    if "activo" in fila:
        fila["activo"] = bool(fila["activo"])
    fila["generos"] = generos
    return fila


def _con_generos(filas):
    generos = repo.generos_por_pelicula([f["id_pelicula"] for f in filas])
    return [_serializar(f, generos.get(f["id_pelicula"], [])) for f in filas]


def _completa(id_pelicula):
    fila = repo.buscar_por_id(id_pelicula)
    return _con_generos([fila])[0] if fila else None


def listar_vigentes(genero=None, texto=None, limite_texto=None):
    """Cartelera: peliculas vigentes. Sin `limite_texto` devuelve todas; con el, un maximo de 50."""
    limite = None
    if limite_texto is not None:
        limite, error = validador.validar_limite(limite_texto)
        if error:
            return None, _con_estado(error)
    return _con_generos(repo.listar_vigentes(genero, texto, limite)), None


def obtener_publica(id_pelicula):
    fila = repo.buscar_activa(id_pelicula)
    if not fila:
        return None, _no_encontrada(id_pelicula)
    return _con_generos([fila])[0], None


def listar_admin(estado=None, texto=None):
    error = validador.validar_estado(estado)
    if error:
        return None, _con_estado(error)
    return _con_generos(repo.listar_admin(estado, texto)), None


def importar(datos):
    """Importa una pelicula de TMDB. Recibe {"id_externo": "603"} y trae el resto desde TMDB."""
    id_externo, opcionales, error = validador.validar_importacion(datos)
    if error:
        return None, _con_estado(error)

    existente = repo.buscar_id_por_externo(id_externo)
    if existente:
        return None, (409, const.ERROR_CODE_DUPLICATE, "Pelicula duplicada",
                      f"Esa pelicula ya esta en el catalogo (id_pelicula {existente})")

    try:
        t = tmdb.detalle(id_externo)
    except tmdb.TmdbError as e:
        codigo = const.ERROR_CODE_NOT_FOUND if e.estado == 404 else const.ERROR_CODE_EXTERNAL_SERVICE
        return None, (e.estado, codigo, "Error al consultar TMDB", e.mensaje)

    nombre = (t.get("title") or "").strip()
    if not nombre:
        return None, (502, const.ERROR_CODE_EXTERNAL_SERVICE, "Error al consultar TMDB",
                      "TMDB no devolvio un titulo para esa pelicula")
    duracion = opcionales.get("duracion_min") or t.get("runtime")
    if not duracion:
        return None, _con_estado(validador.parametro_invalido(
            "TMDB no informa la duracion de esta pelicula; enviar 'duracion_min' en el pedido"))

    nombres_generos = [n for n in (tmdb.nombre_genero(g)[:50] for g in t.get("genres") or []) if n]
    try:
        id_pelicula = repo.crear_con_generos(
            id_externo, nombre[:255], (t.get("overview") or "").strip() or None,
            tmdb.url_poster(t.get("poster_path")), duracion, tmdb.clasificacion_argentina(t),
            opcionales.get("cartelera_desde"), opcionales.get("cartelera_hasta"),
            opcionales.get("activo", 1), nombres_generos)
    except Exception as e:
        if getattr(e, "errno", None) == 1062:  
            return None, (409, const.ERROR_CODE_DUPLICATE, "Pelicula duplicada",
                          "Esa pelicula ya esta en el catalogo")
        raise
    return _completa(id_pelicula), None


def editar(id_pelicula, datos):
    """Modifica datos o periodo de cartelera. `generos` (lista de nombres) REEMPLAZA los actuales."""
    limpio, generos, error = validador.validar_edicion(datos)
    if error:
        return None, _con_estado(error)

    actual = repo.obtener_periodo(id_pelicula)
    if not actual:
        return None, _no_encontrada(id_pelicula, solo_activas=False)

    desde = a_fecha(limpio.get("cartelera_desde", actual["cartelera_desde"]))
    hasta = a_fecha(limpio.get("cartelera_hasta", actual["cartelera_hasta"]))
    if desde and hasta and hasta < desde:
        return None, _con_estado(validador.parametro_invalido(
            "'cartelera_hasta' no puede ser anterior a 'cartelera_desde'"))

    nombres = None
    if generos is not None:
        nombres = list(dict.fromkeys(g.strip() for g in generos if g.strip()))
    faltan = repo.actualizar(id_pelicula, limpio, nombres)
    if faltan:
        return None, _con_estado(validador.parametro_invalido(f"Generos inexistentes: {', '.join(faltan)}"))
    return _completa(id_pelicula), None


def dar_de_baja(id_pelicula):
    """Baja logica: activo = 0. No borra nada."""
    activo = repo.obtener_activo(id_pelicula)
    if activo is None:
        return None, _no_encontrada(id_pelicula, solo_activas=False)
    if activo:
        repo.dar_de_baja(id_pelicula)
    return {"id_pelicula": id_pelicula, "activo": False}, None
