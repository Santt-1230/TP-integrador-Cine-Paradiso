from flask import Blueprint, flash, redirect, render_template, request, url_for

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


@admin_peliculas_bp.get("/admin/peliculas/nueva")
@api.admin_front_requerido
def nueva():
    """Busca títulos en TMDB (?q=, ?pagina=) y muestra los resultados para importar."""
    texto = request.args.get("q", "").strip()
    try:
        pagina = max(1, int(request.args.get("pagina", 1)))
    except ValueError:
        pagina = 1

    resultados = []
    total_paginas = 0
    error = None
    if texto:
        codigo, datos = api.get("/api/catalogo-externo/peliculas", {"q": texto, "pagina": pagina})
        redireccion = api.verificar_estado(codigo)
        if redireccion:
            return redireccion
        if codigo == 200 and isinstance(datos, dict):
            resultados = datos.get("resultados", [])
            total_paginas = datos.get("total_paginas", 0)
        else:
            error = api.mensaje_error(datos)

    return render_template(
        "admin_pelicula_nueva.html",
        q=texto, pagina=pagina, total_paginas=total_paginas, resultados=resultados, error=error,
    )


@admin_peliculas_bp.post("/admin/peliculas/importar")
@api.admin_front_requerido
def importar():
    """Importa la película elegida. Las fechas de cartelera y la duración son opcionales."""
    texto = request.form.get("q", "")
    pagina = request.form.get("pagina", 1)
    volver = redirect(url_for("admin_peliculas.nueva", q=texto, pagina=pagina))

    datos = {"id_externo": request.form.get("id_externo", "").strip()}
    for campo in ("cartelera_desde", "cartelera_hasta"):
        valor = request.form.get(campo, "").strip()
        if valor:
            datos[campo] = valor

    duracion = request.form.get("duracion_min", "").strip()
    if duracion:
        try:
            datos["duracion_min"] = int(duracion)
        except ValueError:
            flash("La duración tiene que ser un número entero de minutos.", "error")
            return volver

    codigo, respuesta = api.pedir("POST", "/api/peliculas", datos)
    redireccion = api.verificar_estado(codigo)
    if redireccion:
        return redireccion
    if codigo != 201:
        flash(api.mensaje_error(respuesta), "error")
        return volver

    nombre = respuesta.get("nombre", "La película") if isinstance(respuesta, dict) else "La película"
    flash(f"«{nombre}» se importó correctamente.", "success")
    return redirect(url_for("admin_peliculas.listado"))
