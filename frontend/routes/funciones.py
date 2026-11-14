from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

import api

funciones_front_bp = Blueprint("funciones_front", __name__)


def datos_formulario_funcion(filtros=None):
    filtros = filtros or {}

    local_id = filtros.get("local_id") or filtros.get("id_local")

    filtros_funciones = {"incluir_canceladas": "true"}
    if local_id:
        filtros_funciones["local_id"] = local_id
    for campo in ("id_sala", "fecha"):
        if filtros.get(campo):
            filtros_funciones[campo] = filtros[campo]

    criterios_completos = (
        all(filtros_funciones.get(campo) for campo in ("local_id", "id_sala", "fecha"))
        and filtros.get("actualizar_funciones") == "1"
    )

    if criterios_completos:
        respuesta_funciones = api.pedir("GET", "/api/funciones", params=filtros_funciones)
    else:
        respuesta_funciones = (200, {"funciones": []})

    respuestas = {
        "peliculas": api.pedir("GET", "/api/admin/peliculas"),
        "locales": api.pedir("GET", "/api/locales"),
        "funciones": respuesta_funciones,
    }

    errores = []
    for estado, respuesta in respuestas.values():
        if estado != 200:
            mensaje = api.mensaje_error(respuesta)
            if mensaje not in errores:
                errores.append(mensaje)

    estado, respuesta = respuestas["peliculas"]
    peliculas = []
    if estado == 200:
        peliculas = [
            {
                "id_pelicula": pelicula.get("id_pelicula"),
                "titulo": pelicula.get("nombre", ""),
                "duracion_minutos": pelicula.get("duracion_min"),
            }
            for pelicula in respuesta.get("peliculas", [])
        ]

    estado, respuesta = respuestas["locales"]
    locales = respuesta.get("locales", []) if estado == 200 else []

    salas = []
    try:
        id_local = int(local_id) if local_id else None
    except (TypeError, ValueError):
        id_local = None

    if id_local:
        estado, respuesta = api.pedir("GET", f"/api/locales/{id_local}/salas")
        if estado == 200:
            salas = [
                {
                    "id_sala": sala.get("id_sala"),
                    "id_local": id_local,
                    "nombre": f"Sala {sala.get('numero_sala')}",
                    "capacidad": sala.get("capacidad"),
                }
                for sala in respuesta.get("salas", [])
            ]
        else:
            errores.append(api.mensaje_error(respuesta))

    estado, respuesta = respuestas["funciones"]
    funciones_existentes = respuesta.get("funciones", []) if estado == 200 else []

    for funcion in funciones_existentes:
        for campo, salida in (
            ("fecha_hora_inicio", "inicio_legible"),
            ("fecha_hora_fin", "fin_legible"),
        ):
            valor = funcion.get(campo)
            try:
                funcion[salida] = datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
            except (TypeError, ValueError):
                funcion[salida] = valor or "Horario no disponible"

    return {
        "peliculas": peliculas,
        "locales": locales,
        "salas": salas,
        "funciones_existentes": funciones_existentes,
        "funciones_consultadas": criterios_completos,
        "error_opciones": "; ".join(errores) if errores else None,
    }


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
    cantidad_columnas = max((sum(1 for butaca in butacas if butaca.get("fila") == fila) for fila in {butaca.get("fila") for butaca in butacas}), default=0,)
    error = None if estado == 200 else api.mensaje_error(datos)
    return render_template(
        "funcion_butacas.html", id_funcion=id_funcion, butacas=butacas,
        cantidad_columnas=cantidad_columnas,
        error=error
    ), estado if estado >= 500 else 200


@funciones_front_bp.route("/admin/funciones", methods=["GET"])
@api.admin_front_requerido
def admin_funciones():
    estado, datos = api.pedir(
        "GET", "/api/funciones", params={"incluir_canceladas": "true"}
    )
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion

    funciones = datos.get("funciones", []) if estado == 200 else []
    error = None if estado == 200 else api.mensaje_error(datos)
    return render_template(
        "admin_funciones.html", funciones=funciones, error=error
    )


@funciones_front_bp.route("/admin/funciones/nueva", methods=["GET", "POST"])
@api.admin_front_requerido
def admin_nueva_funcion():
    error = None
    valores = request.form if request.method == "POST" else request.args

    if request.method == "POST" and request.form.get("actualizar_funciones") != "1":
        datos = {
            "id_pelicula": request.form.get("id_pelicula"),
            "id_sala": request.form.get("id_sala"),
            "fecha_hora_inicio": request.form.get("fecha_hora_inicio"),
            "precio_entrada": request.form.get("precio_entrada"),
        }

        estado, respuesta = api.pedir("POST", "/api/funciones", datos=datos)

        redireccion = api.verificar_estado(estado)
        if redireccion:
            return redireccion

        if estado == 201:
            return redirect(url_for("funciones_front.admin_funciones"))

        error = api.mensaje_error(respuesta)

    opciones = datos_formulario_funcion(valores)
    error = error or opciones.pop("error_opciones")

    return render_template(
        "funcion_form.html",
        funcion=None,
        error=error,
        valores=valores,
        **opciones,
    )


@funciones_front_bp.route("/admin/funciones/<int:id_funcion>/editar", methods=["GET", "POST"])
@api.admin_front_requerido
def admin_editar_funcion(id_funcion):
    error = None
    funcion = None
    valores = request.form if request.method == "POST" else request.args

    if request.method == "POST" and request.form.get("actualizar_funciones") != "1":
        datos = {
            campo: request.form.get(campo)
            for campo in ("id_pelicula", "id_sala", "fecha_hora_inicio", "precio_entrada")
            if request.form.get(campo)
        }

        estado, respuesta = api.pedir("PATCH", f"/api/funciones/{id_funcion}", datos=datos)

        redireccion = api.verificar_estado(estado)
        if redireccion:
            return redireccion

        if estado == 200:
            return redirect(url_for("funciones_front.admin_funciones"))

        error = api.mensaje_error(respuesta)

    estado, respuesta = api.pedir("GET", f"/api/funciones/{id_funcion}")

    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion

    if estado == 200:
        funcion = respuesta.get("funcion")
    elif error is None:
        error = api.mensaje_error(respuesta)

    if not valores.get("id_local") and funcion:
        valores = {
            **funcion,
            **dict(valores),
            "id_local": funcion.get("id_local"),
        }

    opciones = datos_formulario_funcion(valores)
    error = error or opciones.pop("error_opciones")

    return render_template(
        "funcion_form.html",
        funcion=funcion,
        error=error,
        valores=valores,
        **opciones,
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