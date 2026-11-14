from datetime import date, datetime

from flask import Blueprint, redirect, render_template, request, url_for

import api


peliculas_front_bp = Blueprint("peliculas_front", __name__)

POR_PAGINA = 8

DIAS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo"
]

# Pantalla de elección de butacas de una función.
# Si cambia la ruta, se modifica solamente acá.
URL_COMPRA = "/funciones/{id_funcion}/butacas"


# ====================================
# MANEJO DE ERRORES
# ====================================

def error_backend(estado, datos):

    return render_template(
        "error.html",
        estado=estado,
        mensaje=api.mensaje_error(datos)
    ), estado


def error_formato():

    return render_template(
        "error.html",
        estado=502,
        mensaje="El servidor devolvió una respuesta con un formato inválido."
    ), 502


# ====================================
# FILTROS DE FECHA Y PRECIO
# ====================================

@peliculas_front_bp.app_template_filter("fecha_ar")
def fecha_ar(valor):
    """
    '2026-10-31' -> '31/10/2026'.
    Si no es una fecha válida, devuelve el valor tal cual.
    """

    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")

    except (TypeError, ValueError):
        return valor


@peliculas_front_bp.app_template_filter("precio_ar")
def precio_ar(valor):
    """
    5500.0 -> '$5.500'.
    5500.5 -> '$5.500,50'.
    """

    try:
        numero = float(valor)

    except (TypeError, ValueError):
        return valor

    texto = (
        f"{numero:,.0f}"
        if numero == int(numero)
        else f"{numero:,.2f}"
    )

    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ====================================
# AGRUPAR FUNCIONES POR DÍA
# ====================================

def agrupar_por_dia(funciones):

    por_fecha = {}

    for f in funciones:

        try:
            inicio = datetime.fromisoformat(
                f["fecha_hora_inicio"]
            )

            fin = datetime.fromisoformat(
                f["fecha_hora_fin"]
            )

        except (KeyError, TypeError, ValueError):
            continue

        por_fecha.setdefault(inicio.date(), []).append(
            dict(
                f,
                hora_inicio=inicio.strftime("%H:%M"),
                hora_fin=fin.strftime("%H:%M"),
                url_compra=URL_COMPRA.format(
                    id_funcion=f.get("id_funcion")
                )
            )
        )

    return [
        {
            "dia": f"{DIAS[d.weekday()]} {d.strftime('%d/%m/%Y')}",
            "funciones": fs
        }
        for d, fs in sorted(por_fecha.items())
    ]


# ====================================
# OBTENER LISTA DE PELÍCULAS
# ====================================

def obtener_peliculas(params=None):

    estado, respuesta = api.get(
        "/api/peliculas",
        params
    )

    if estado != 200:
        return None, error_backend(estado, respuesta)

    if (
        not isinstance(respuesta, dict)
        or not isinstance(respuesta.get("peliculas"), list)
    ):
        return None, error_formato()

    return respuesta["peliculas"], None


# ====================================
# PÁGINA DE INICIO
# ====================================

@peliculas_front_bp.get("/")
def inicio():

    peliculas, error = obtener_peliculas(
        {"limite": POR_PAGINA}
    )

    if error:
        return error

    # Si los endpoints de promociones o servicios fallan,
    # las secciones simplemente se muestran vacías.

    promociones = api.get_lista(
        "/api/promociones",
        "promociones"
    )

    productos = api.get_lista(
        "/api/servicios",
        "servicios"
    )

    return render_template(
        "inicio.html",
        peliculas=peliculas,
        promociones=promociones,
        productos=productos
    )


# ====================================
# LISTADO DE PELÍCULAS
# ====================================

@peliculas_front_bp.get("/buscar")
def buscar():
    """Buscador del encabezado: redirige a la cartelera con el texto buscado."""
    texto = request.args.get("q", "").strip()
    if not texto:
        return redirect(url_for("peliculas_front.lista"))
    return redirect(url_for("peliculas_front.lista", q=texto))


@peliculas_front_bp.get("/peliculas")
def lista():

    genero = request.args.get("genero", "").strip()
    texto = request.args.get("q", "").strip()

    try:
        mostrar = int(
            request.args.get("mostrar", POR_PAGINA)
        )

    except ValueError:
        mostrar = POR_PAGINA

    mostrar = max(
        POR_PAGINA,
        min(mostrar, 200)
    )

    filtros = {
        clave: valor
        for clave, valor in (
            ("genero", genero),
            ("q", texto)
        )
        if valor
    }

    # Obtener películas aplicando los filtros.
    peliculas, error = obtener_peliculas(filtros)

    if error:
        return error

    # Las opciones del selector salen de la lista sin filtrar,
    # para no perder géneros al aplicar un filtro.

    if filtros:

        todas, error = obtener_peliculas()

        if error:
            return error

    else:
        todas = peliculas

    generos = sorted({
        g
        for p in todas
        for g in (p.get("generos") or [])
    })

    return render_template(
        "peliculas.html",
        peliculas=peliculas[:mostrar],
        hay_mas=len(peliculas) > mostrar,
        siguiente=mostrar + POR_PAGINA,
        generos=generos,
        genero=genero,
        q=texto
    )


# ====================================
# DETALLE DE UNA PELÍCULA
# ====================================

@peliculas_front_bp.get("/peliculas/<int:id_pelicula>")
def detalle(id_pelicula):

    # Obtener película seleccionada.

    estado, pelicula = api.get(
        f"/api/peliculas/{id_pelicula}"
    )

    if estado != 200:
        return error_backend(estado, pelicula)

    # Obtener otras películas para recomendar.

    otras = api.get_lista(
        "/api/peliculas",
        "peliculas",
        {"limite": 4}
    )

    mas_para_ver = [
        p
        for p in otras
        if p["id_pelicula"] != id_pelicula
    ][:3]

    # Obtener funciones disponibles.
    # Si el endpoint falla, se muestra la película igualmente.

    funciones = api.get_lista(
        "/api/funciones",
        "funciones",
        {"pelicula_id": id_pelicula}
    )

    funciones = agrupar_por_dia(funciones)

    return render_template(
        "pelicula_detalle.html",
        p=pelicula,
        mas=mas_para_ver,
        funciones=funciones
    )
