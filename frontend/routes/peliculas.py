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

URL_COMPRA = "/funciones/{id_funcion}/butacas"


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


@peliculas_front_bp.app_template_filter("fecha_ar")
def fecha_ar(valor):

    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")

    except (TypeError, ValueError):
        return valor


@peliculas_front_bp.app_template_filter("precio_ar")
def precio_ar(valor):

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


CANTIDAD_CARRUSEL = 4


def _fecha_funcion(texto):
    try:
        return datetime.fromisoformat(str(texto).replace(" ", "T"))
    except ValueError:
        return None


def _proximas_funciones():
    proximas = {}
    ahora = datetime.now()
    filtros = {}
    cine_id = api.session.get("cine_id")
    if cine_id:
        filtros["local_id"] = cine_id
    for f in api.get_lista("/api/funciones", "funciones", filtros or None):
        if f.get("estado") in ("cancelada", "finalizada"):
            continue
        inicio = _fecha_funcion(f.get("fecha_hora_inicio"))
        if not inicio or inicio < ahora:
            continue
        id_pelicula = f.get("id_pelicula")
        if id_pelicula not in proximas or inicio < proximas[id_pelicula]:
            proximas[id_pelicula] = inicio
    return proximas


def _generos_texto(generos):
    if isinstance(generos, str):
        return generos
    nombres = [g.get("nombre") if isinstance(g, dict) else g for g in generos or []]
    return ", ".join(n for n in nombres if n)


def _destacadas(peliculas):
    todas, _ = obtener_peliculas({"limite": 50})
    candidatas = todas or peliculas
    proximas = _proximas_funciones()

    con_funcion = sorted(
        (p for p in candidatas if p.get("id_pelicula") in proximas),
        key=lambda p: proximas[p["id_pelicula"]],
    )
    sin_funcion = sorted(
        (p for p in candidatas if p.get("id_pelicula") not in proximas),
        key=lambda p: p.get("cartelera_desde") or "",
        reverse=True,
    )

    destacadas = []
    por_cine = bool(api.session.get("cine_id"))
    for p in con_funcion + ([] if por_cine else sin_funcion):
        item = dict(p)
        inicio = proximas.get(p.get("id_pelicula"))
        item["proxima_funcion"] = inicio.strftime("%d/%m %H:%M") if inicio else None
        item["generos_txt"] = _generos_texto(p.get("generos"))
        sinopsis = (p.get("sinopsis") or "").strip()
        item["sinopsis_corta"] = sinopsis if len(sinopsis) <= 230 else sinopsis[:230].rsplit(" ", 1)[0] + "…"
        destacadas.append(item)
    return destacadas[:CANTIDAD_CARRUSEL]


@peliculas_front_bp.get("/")
def inicio():

    peliculas, error = obtener_peliculas(
        {"limite": POR_PAGINA}
    )

    if error:
        return error

    destacadas = _destacadas(peliculas)

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
        destacadas=destacadas,
        promociones=promociones,
        productos=productos
    )

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

    peliculas, error = obtener_peliculas(filtros)

    if error:
        return error

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


@peliculas_front_bp.get("/peliculas/<int:id_pelicula>")
def detalle(id_pelicula):

    estado, pelicula = api.get(
        f"/api/peliculas/{id_pelicula}"
    )

    if estado != 200:
        return error_backend(estado, pelicula)

    if not api.session.get("cine_id"):
        api.session["pelicula_pendiente_id"] = id_pelicula
        return redirect(url_for("locales.mostrar_locales"))

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

    filtros_funciones = {
        "pelicula_id": id_pelicula
    }
    cine_id = api.session.get("cine_id")
    if cine_id:
        filtros_funciones["local_id"] = cine_id

    funciones = api.get_lista(
        "/api/funciones",
        "funciones",
        filtros_funciones
    )

    funciones = agrupar_por_dia(funciones)

    return render_template(
        "pelicula_detalle.html",
        p=pelicula,
        mas=mas_para_ver,
        funciones=funciones
    )
