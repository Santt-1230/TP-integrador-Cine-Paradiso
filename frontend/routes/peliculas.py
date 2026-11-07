from datetime import date, datetime

from flask import Blueprint, render_template, request

import api

peliculas_front_bp = Blueprint("peliculas_front", __name__)

POR_PAGINA = 8
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
# Pantalla de eleccion de butacas de una funcion (modulo de Max). Si se llama distinto, se cambia solo aca.
URL_COMPRA = "/funciones/{id_funcion}/butacas"


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


@peliculas_front_bp.app_template_filter("precio_ar")
def precio_ar(valor):
    """5500.0 -> '$5.500'. Con centavos: 5500.5 -> '$5.500,50'."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return valor
    texto = f"{numero:,.0f}" if numero == int(numero) else f"{numero:,.2f}"
    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def agrupar_por_dia(funciones):
    """[{'dia': 'Viernes 20/11/2026', 'funciones': [...]}], ordenado por fecha. Salta las filas con fecha invalida."""
    por_fecha = {}
    for f in funciones:
        try:
            inicio = datetime.fromisoformat(f["fecha_hora_inicio"])
            fin = datetime.fromisoformat(f["fecha_hora_fin"])
        except (KeyError, TypeError, ValueError):
            continue
        por_fecha.setdefault(inicio.date(), []).append(dict(
            f, hora_inicio=inicio.strftime("%H:%M"), hora_fin=fin.strftime("%H:%M"),
            url_compra=URL_COMPRA.format(id_funcion=f.get("id_funcion"))))
    return [{"dia": f"{DIAS[d.weekday()]} {d.strftime('%d/%m/%Y')}", "funciones": fs}
            for d, fs in sorted(por_fecha.items())]


@peliculas_front_bp.get("/")
def inicio():
    peliculas = api.get("/api/peliculas", {"limite": POR_PAGINA})["peliculas"]
    # Los modulos de Euge (P7). Si su endpoint todavia no existe, la seccion simplemente no se muestra.
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
    # Si el backend no responde o no hay funciones, la pelicula se muestra igual (get_lista devuelve []).
    funciones = agrupar_por_dia(api.get_lista("/api/funciones", "funciones", {"pelicula_id": id_pelicula}))
    return render_template("pelicula_detalle.html", p=pelicula, mas=mas_para_ver, funciones=funciones)
