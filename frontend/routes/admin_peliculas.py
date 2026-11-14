from flask import Blueprint, render_template, request

import api

admin_peliculas_bp = Blueprint("admin_peliculas", __name__)

# Estado de cartelera que calcula el backend -> texto para mostrar.
ESTADOS = {
    "vigente": "Vigente",
    "proxima": "Próxima",
    "vencida": "Vencida",
    "inactiva": "Inactiva",
}


@admin_peliculas_bp.get("/admin/peliculas")
@api.admin_front_requerido
def listado():
    """Todas las películas del catálogo. Filtros opcionales: ?estado= y ?q=."""
    estado = request.args.get("estado", "").strip()
    texto = request.args.get("q", "").strip()
    filtros = {clave: valor for clave, valor in (("estado", estado), ("q", texto)) if valor}

    codigo, datos = api.get("/api/admin/peliculas", filtros)
    redireccion = api.verificar_estado(codigo)
    if redireccion:
        return redireccion

    peliculas = []
    error = None
    if codigo == 200 and isinstance(datos, dict):
        peliculas = datos.get("peliculas", [])
    else:
        error = api.mensaje_error(datos)

    return render_template(
        "admin_peliculas.html",
        peliculas=peliculas, error=error, estados=ESTADOS, estado=estado, q=texto,
    )
