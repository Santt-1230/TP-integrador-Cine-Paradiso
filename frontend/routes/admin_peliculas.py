from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

import api

admin_peliculas_bp = Blueprint("admin_peliculas", __name__)

ESTADOS = {
    "vigente": "Vigente",
    "proxima": "Próxima",
    "vencida": "Vencida",
    "inactiva": "Inactiva",
}


@admin_peliculas_bp.get("/admin/peliculas")
@api.admin_front_requerido
def listado():
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


def _fecha(texto):
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


def _cambios_de_estado(estado, desde_txt, hasta_txt):
    desde, hasta = _fecha(desde_txt), _fecha(hasta_txt)
    if (desde_txt and not desde) or (hasta_txt and not hasta):
        return None, "Revisá las fechas, alguna no es válida."

    hoy = date.today()
    if estado == "inactiva":
        return None, None

    if estado == "vigente":
        if hasta and hasta < hoy:
            return None, "Con ese fin la película ya estaría vencida. Dejá 'Hasta' vacío o poné una fecha futura."
        
        return {
            "activo": True,
            "cartelera_desde": desde_txt if desde and desde <= hoy else None,
            "cartelera_hasta": hasta_txt or None,
        }, None

    if estado == "proxima":
        if not desde or desde <= hoy:
            return None, "Para Próxima, poné en 'Desde' una fecha que todavía no llegó."
        return {
            "activo": True,
            "cartelera_desde": desde_txt,
            "cartelera_hasta": hasta_txt or None,
        }, None

    return None, "Elegí un estado."


@admin_peliculas_bp.route("/admin/peliculas/<int:id_pelicula>/estado", methods=["GET", "POST"])
@api.admin_front_requerido
def cambiar_estado(id_pelicula):
    codigo, datos = api.get("/api/admin/peliculas")
    redireccion = api.verificar_estado(codigo)
    if redireccion:
        return redireccion
    peliculas = datos.get("peliculas", []) if codigo == 200 and isinstance(datos, dict) else []
    pelicula = next((p for p in peliculas if p.get("id_pelicula") == id_pelicula), None)
    if pelicula is None:
        flash("No se encontró la película.", "error")
        return redirect(url_for("admin_peliculas.listado"))

    if request.method == "POST":
        estado = request.form.get("estado", "")
        cambios, error = _cambios_de_estado(
            estado,
            request.form.get("cartelera_desde", "").strip(),
            request.form.get("cartelera_hasta", "").strip(),
        )
        if error:
            flash(error, "error")
            return redirect(url_for("admin_peliculas.cambiar_estado", id_pelicula=id_pelicula))

        if estado == "inactiva":
            codigo, respuesta = api.pedir("DELETE", f"/api/peliculas/{id_pelicula}")
        else:
            codigo, respuesta = api.pedir("PATCH", f"/api/peliculas/{id_pelicula}", cambios)
        redireccion = api.verificar_estado(codigo)
        if redireccion:
            return redireccion
        if codigo != 200:
            flash(api.mensaje_error(respuesta), "error")
            return redirect(url_for("admin_peliculas.cambiar_estado", id_pelicula=id_pelicula))

        flash(f"Se actualizó el estado de «{pelicula.get('nombre', 'la película')}».", "success")
        return redirect(url_for("admin_peliculas.listado"))

    return render_template("admin_pelicula_estado.html", pelicula=pelicula, estados=ESTADOS)
