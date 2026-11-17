"""Cliente minimo de TMDB. La clave va en TMDB_API_KEY (archivo .env)."""
import logging
import os

import requests

logger = logging.getLogger(__name__)

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
IDIOMA = "es-AR"


class TmdbError(Exception):
    def __init__(self, mensaje, estado=502):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.estado = estado


def _get(ruta, **params):
    clave = os.getenv("TMDB_API_KEY")
    if not clave:
        raise TmdbError("Falta configurar TMDB_API_KEY en el servidor", 503)
    try:
        r = requests.get(
            f"{BASE}{ruta}",
            params={"api_key": clave, "language": IDIOMA, **params},
            timeout=10,
        )
    except requests.RequestException:
        logger.exception("No se pudo conectar con TMDB")
        raise TmdbError("No se pudo conectar con TMDB", 502)
    if r.status_code == 404:
        raise TmdbError("No existe en TMDB", 404)
    if r.status_code == 401:
        raise TmdbError("La clave de TMDB es invalida", 502)
    if not r.ok:
        raise TmdbError(f"TMDB respondio con error {r.status_code}", 502)
    return r.json()


def buscar(texto, pagina=1):
    return _get("/search/movie", query=texto, page=pagina, include_adult="false")


def detalle(id_tmdb):
    return _get(f"/movie/{id_tmdb}", append_to_response="release_dates")


# Generos de TMDB (por su id, que no cambia) con el nombre en español que usa el sitio.
GENEROS_ES = {
    28: "Acción", 12: "Aventura", 16: "Animación", 35: "Comedia", 80: "Crimen",
    99: "Documental", 18: "Drama", 10751: "Familia", 14: "Fantasía", 36: "Historia",
    27: "Terror", 10402: "Música", 9648: "Misterio", 10749: "Romance",
    878: "Ciencia ficción", 10770: "Película de TV", 53: "Suspenso", 10752: "Bélica",
    37: "Western",
}


def nombre_genero(genero):
    """Nombre en español de un genero de TMDB ({"id":..., "name":...}). Si no esta en la tabla, usa el de TMDB."""
    return GENEROS_ES.get(genero.get("id")) or (genero.get("name") or "").strip()


def url_poster(path):
    return f"{IMG}{path}" if path else None


def clasificacion_argentina(datos):
    paises = (datos.get("release_dates") or {}).get("results") or []
    for pais in paises:
        if pais.get("iso_3166_1") == "AR":
            for fecha in pais.get("release_dates") or []:
                cert = (fecha.get("certification") or "").strip()
                if cert:
                    if cert.isdigit():
                        cert = "+" + cert
                    return cert[:20]
    return None
