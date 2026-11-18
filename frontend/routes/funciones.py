from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, request, url_for

import api

funciones_front_bp = Blueprint("funciones_front", __name__)


def obtener_salas_activas():
    estado, respuesta = api.pedir("GET", "/api/locales")
    if estado != 200:
        return [], api.mensaje_error(respuesta)

    salas = []
    for local in respuesta.get("locales", []):
        estado, datos = api.pedir(
            "GET", f"/api/locales/{local['id_local']}/salas"
        )
        if estado != 200:
            return [], api.mensaje_error(datos)

        for sala in datos.get("salas", []):
            sala["nombre_local"] = local["nombre"]
            salas.append(sala)

    return salas, None


def obtener_peliculas_programables():
    estado, datos = api.pedir("GET", "/api/admin/peliculas")
    if estado != 200 or not isinstance(datos, dict):
        return []
    return [p for p in datos.get("peliculas", []) if p.get("estado_cartelera") in ("vigente", "proxima")]


NOMBRES_CAMPOS = {
    "id_pelicula": "la película",
    "id_sala": "la sala",
    "fecha_hora_inicio": "la fecha y hora de inicio",
    "precio_entrada": "el precio de entrada",
}


def _legible(texto):
    if not texto:
        return texto
    for campo, nombre in NOMBRES_CAMPOS.items():
        texto = texto.replace(campo, nombre)
    return texto[0].upper() + texto[1:]


def _inicio_funcion():
    # el backend pide fecha futura, por eso "ahora" es dentro de 2 minutos
    if request.form.get("empieza_ahora"):
        return (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M")
    return request.form.get("fecha_hora_inicio")




def _fecha_hora(texto):
    try:
        return datetime.fromisoformat(str(texto).replace(" ", "T")).replace(tzinfo=None)
    except ValueError:
        return None


def _situacion_funcion(funcion):
    ahora = datetime.now()
    inicio = _fecha_hora(funcion.get("fecha_hora_inicio"))
    fin = _fecha_hora(funcion.get("fecha_hora_fin"))
    if funcion.get("estado") == "finalizada" or (fin and fin <= ahora):
        return "Finalizada"
    if inicio and inicio <= ahora:
        return "En curso"
    return "Programada"


def _preparar_funciones_admin(funciones):
    # las canceladas no se muestran; las demás van con su situación
    orden = {"En curso": 0, "Programada": 1, "Finalizada": 2}
    visibles = []
    for funcion in funciones:
        if funcion.get("estado") == "cancelada":
            continue
        funcion["situacion"] = _situacion_funcion(funcion)
        visibles.append(funcion)
    visibles.sort(key=lambda f: (orden[f["situacion"]], str(f.get("fecha_hora_inicio"))))
    return visibles


@funciones_front_bp.route("/funciones", methods=["GET"])
def pagina_funciones():
    estado, datos = api.pedir_api("GET", "/api/funciones", params=request.args)
    funciones = datos.get("funciones", []) if estado == 200 else []
    error = None if estado == 200 else api.mensaje_error(datos)
    return render_template(
        "funciones.html", funciones=funciones, filtros=request.args,
        error=error
    )


@funciones_front_bp.route("/funciones/<int:id_funcion>/butacas", methods=["GET"])
def pagina_butacas(id_funcion):
    estado, datos = api.pedir_api(
        "GET", f"/api/funciones/{id_funcion}/butacas"
    )
    butacas = datos.get("butacas", []) if estado == 200 else []
    cantidad_columnas = max(
        (sum(1 for butaca in butacas if butaca.get("fila") == fila)
         for fila in {butaca.get("fila") for butaca in butacas}),
        default=0,
    )
    error = None if estado == 200 else api.mensaje_error(datos)
    return render_template(
        "funcion_butacas.html", id_funcion=id_funcion, butacas=butacas,
        cantidad_columnas=cantidad_columnas,
        error=error
    ), estado if estado >= 500 else 200


@funciones_front_bp.route("/admin/funciones", methods=["GET"])
@api.admin_front_requerido
def admin_funciones():
    estado, datos = api.pedir("GET", "/api/funciones", params={"incluir_canceladas": "true"})
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion

    funciones = datos.get("funciones", []) if estado == 200 else []
    funciones = _preparar_funciones_admin(funciones)
    error = None if estado == 200 else api.mensaje_error(datos)
    return render_template(
        "admin_funciones.html", funciones=funciones, error=error
    )


@funciones_front_bp.route("/admin/funciones/nueva", methods=["GET", "POST"])
@api.admin_front_requerido
def admin_nueva_funcion():
    error = None
    if request.method == "POST":
        datos = {
            "id_pelicula": request.form.get("id_pelicula"),
            "id_sala": request.form.get("id_sala"),
            "fecha_hora_inicio": _inicio_funcion(),
            "precio_entrada": request.form.get("precio_entrada"),
        }
        estado, respuesta = api.pedir(
            "POST", "/api/funciones", datos=datos
        )
        redireccion = api.verificar_estado(estado)
        if redireccion:
            return redireccion
        if estado == 201:
            return redirect(url_for("funciones_front.admin_funciones"))
        error = api.mensaje_error(respuesta)

    salas, error_salas = obtener_salas_activas()
    if error is None:
        error = error_salas
    return render_template(
        "funcion_form.html", funcion=None, error=_legible(error),
        salas=salas, peliculas=obtener_peliculas_programables()
    )


@funciones_front_bp.route("/admin/funciones/<int:id_funcion>/editar", methods=["GET", "POST"])
@api.admin_front_requerido
def admin_editar_funcion(id_funcion):
    error = None
    funcion = None

    if request.method == "POST":
        datos = {}
        for campo in (
            "id_pelicula", "id_sala", "fecha_hora_inicio", "precio_entrada"
        ):
            valor = request.form.get(campo)
            if valor:
                datos[campo] = valor
        estado, respuesta = api.pedir(
            "PATCH", f"/api/funciones/{id_funcion}", datos=datos
        )
        redireccion = api.verificar_estado(estado)
        if redireccion:
            return redireccion
        if estado == 200:
            return redirect(url_for("funciones_front.admin_funciones"))
        error = api.mensaje_error(respuesta)

    estado, respuesta = api.pedir(
        "GET", f"/api/funciones/{id_funcion}"
    )
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion
    if estado == 200:
        funcion = respuesta.get("funcion")
    elif error is None:
        error = api.mensaje_error(respuesta)

    salas, error_salas = obtener_salas_activas()
    if error is None:
        error = error_salas
    return render_template(
        "funcion_form.html", funcion=funcion, error=_legible(error),
        salas=salas, peliculas=obtener_peliculas_programables()
    )


@funciones_front_bp.route("/admin/funciones/<int:id_funcion>/cancelar", methods=["POST"])
@api.admin_front_requerido
def admin_cancelar_funcion(id_funcion):
    estado, respuesta = api.pedir(
        "PATCH", f"/api/funciones/{id_funcion}", datos={"estado": "cancelada"}
    )
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion
    if estado != 200:
        return render_template(
            "admin_funciones.html", funciones=[],
            error=api.mensaje_error(respuesta)
        )
    return redirect(url_for("funciones_front.admin_funciones"))
