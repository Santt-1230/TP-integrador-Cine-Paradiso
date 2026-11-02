import constants as const
import tmdb
from repositories import peliculas as repo
from validators import peliculas as validador


def buscar(texto, pagina):
    """Busca titulos en TMDB y marca cuales ya estan en el catalogo propio. Devuelve (resultado, error)."""
    texto, pagina, error = validador.validar_busqueda_externa(texto, pagina)
    if error:
        return None, (400, *error)
    try:
        datos = tmdb.buscar(texto, pagina)
    except tmdb.TmdbError as e:
        codigo = const.ERROR_CODE_NOT_FOUND if e.estado == 404 else const.ERROR_CODE_EXTERNAL_SERVICE
        return None, (e.estado, codigo, "Error al consultar TMDB", e.mensaje)

    resultados = datos.get("results") or []
    importadas = repo.ids_externos_existentes([str(r["id"]) for r in resultados])
    return {
        "pagina": datos.get("page", pagina),
        "total_paginas": datos.get("total_pages", 0),
        "resultados": [
            {
                "id_externo": str(r["id"]),
                "nombre": r.get("title"),
                "nombre_original": r.get("original_title"),
                "fecha_estreno": r.get("release_date") or None,
                "sinopsis": r.get("overview") or None,
                "poster_url": tmdb.url_poster(r.get("poster_path")),
                "ya_importada": str(r["id"]) in importadas,
            }
            for r in resultados
        ],
    }, None
