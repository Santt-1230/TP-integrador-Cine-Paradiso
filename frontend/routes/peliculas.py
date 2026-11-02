from datetime import date

from flask import Blueprint, render_template, request

import api

peliculas_front_bp = Blueprint("peliculas_front", __name__)

POR_PAGINA = 8


@peliculas_front_bp.app_errorhandler(api.ApiError)
def error_del_backend(error):
    return render_template("error.html", estado=error.estado, mensaje=error.mensaje), error.estado


@peliculas_front_bp.app_template_filter("fecha_ar")
def fecha_ar(valor):
    """'2026-10-31' -> '31/10/2026'. Si no es una fecha valida, devuelve el valor tal cual."""
    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor


@peliculas_front_bp.get("/")
def inicio():
    peliculas = api.get("/api/peliculas", {"limite": POR_PAGINA})["peliculas"]
    # Los "productos" del sitio son los servicios del backend (GET /api/servicios).
    promociones = api.get_lista("/api/promociones", "promociones")
    productos = api.get_lista("/api/servicios", "servicios")
    return render_template("inicio.html", peliculas=peliculas, promociones=promociones, productos=productos)


@peliculas_front_bp.get("/peliculas")
def lista():
    genero = request.args.get("genero", "").strip()
    texto = request.args.get("q", "").strip()
    try:
        mostrar = int(request.args.get("mostrar", POR_PAGINA))
    except ValueError:
        mostrar = POR_PAGINA
    mostrar = max(POR_PAGINA, min(mostrar, 200))

    filtros = {k: v for k, v in (("genero", genero), ("q", texto)) if v}
    peliculas = api.get("/api/peliculas", filtros)["peliculas"]
    # Las opciones del selector salen de la lista sin filtrar, para no perder generos al filtrar.
    todas = api.get("/api/peliculas")["peliculas"] if filtros else peliculas
    generos = sorted({g for p in todas for g in p["generos"]})

    return render_template(
        "peliculas.html",
        peliculas=peliculas[:mostrar], hay_mas=len(peliculas) > mostrar,
        siguiente=mostrar + POR_PAGINA, generos=generos, genero=genero, q=texto,
    )


@peliculas_front_bp.get("/peliculas/<int:id_pelicula>")
def detalle(id_pelicula):
    pelicula = api.get(f"/api/peliculas/{id_pelicula}")
    otras = api.get_lista("/api/peliculas", "peliculas", {"limite": 4})
    mas_para_ver = [p for p in otras if p["id_pelicula"] != id_pelicula][:3]
    return render_template("pelicula_detalle.html", p=pelicula, mas=mas_para_ver)
