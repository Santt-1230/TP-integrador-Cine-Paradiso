from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, request, url_for

import api

funciones_front_bp = Blueprint("funciones_front", __name__)


def fecha_hora_legible(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor or "Horario no disponible"


def agregar_horarios_legibles(funciones):
    for funcion in funciones:
        funcion["inicio_legible"] = fecha_hora_legible(
            funcion.get("fecha_hora_inicio")
        )
        funcion["fin_legible"] = fecha_hora_legible(
            funcion.get("fecha_hora_fin")
        )
    return funciones


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

    agregar_horarios_legibles(funciones_existentes)

    return {
        "peliculas": peliculas,
        "locales": locales,
        "salas": salas,
        "funciones_existentes": funciones_existentes,
        "funciones_consultadas": criterios_completos,
        "error_opciones": "; ".join(errores) if errores else None,
    }


def _inicio_funcion():
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
    orden = {"En curso": 0, "Programada": 1, "Finalizada": 2}
    visibles = []
    for funcion in funciones:
        if funcion.get("estado") == "cancelada":
            continue
        funcion["situacion"] = _situacion_funcion(funcion)
        if funcion["situacion"] == "Finalizada":
            continue
        visibles.append(funcion)
    visibles.sort(key=lambda f: (orden[f["situacion"]], str(f.get("fecha_hora_inicio"))))
    return visibles


@funciones_front_bp.route("/funciones", methods=["GET"])
def pagina_funciones():
    filtros = {
        campo: request.args.get(campo, "")
        for campo in ("pelicula_id", "local_id", "fecha")
    }
    parametros_api = {campo: valor for campo, valor in filtros.items() if valor}

    estado, datos = api.pedir_api("GET", "/api/funciones", params=parametros_api)
    funciones = datos.get("funciones", []) if estado == 200 else []
    agregar_horarios_legibles(funciones)
    error = None if estado == 200 else api.mensaje_error(datos)

    estado_peliculas, datos_peliculas = api.pedir_api("GET", "/api/peliculas")
    peliculas = datos_peliculas.get("peliculas", []) if estado_peliculas == 200 else []
    estado_locales, datos_locales = api.pedir_api("GET", "/api/locales")
    locales = datos_locales.get("locales", []) if estado_locales == 200 else []

    if error is None and estado_peliculas != 200:
        error = api.mensaje_error(datos_peliculas)
    if error is None and estado_locales != 200:
        error = api.mensaje_error(datos_locales)

    return render_template(
        "funciones.html",
        funciones=funciones,
        peliculas=peliculas,
        locales=locales,
        filtros=filtros,
        error=error,
    )


@funciones_front_bp.route("/funciones/<int:id_funcion>/butacas", methods=["GET"])
def pagina_butacas(id_funcion):
    checkout_expirado = request.args.get("checkout_expirado") == "1"

    estado, datos = api.pedir("GET", f"/api/funciones/{id_funcion}/butacas")
    butacas = datos.get("butacas", []) if estado == 200 else []
    error = None if estado == 200 else api.mensaje_error(datos)
    cantidad_columnas = max(
        (sum(1 for butaca in butacas if butaca.get("fila") == fila)
         for fila in {butaca.get("fila") for butaca in butacas}),
        default=0,
        )
    return render_template(
        "funcion_butacas.html", id_funcion=id_funcion, butacas=butacas,
        cantidad_columnas=cantidad_columnas,
        error=error,
        checkout_expirado=checkout_expirado,
    ), estado if estado >= 500 else 200


@funciones_front_bp.route("/admin/funciones", methods=["GET"])
@api.admin_front_requerido
def admin_funciones():
    local_id = request.args.get("local_id", "")
    filtros = {"incluir_canceladas": "true"}
    if local_id:
        filtros["local_id"] = local_id

    estado, datos = api.pedir(
        "GET", "/api/funciones", params=filtros
    )
    funciones = datos.get("funciones", []) if estado == 200 else []
    funciones = _preparar_funciones_admin(funciones)
    agregar_horarios_legibles(funciones)
    error = None if estado == 200 else api.mensaje_error(datos)
    estado_locales, datos_locales = api.get("/api/locales")
    locales = datos_locales.get("locales", []) if estado_locales == 200 else []
    if estado_locales != 200 and error is None:
        error = api.mensaje_error(datos_locales)

    return render_template(
        "admin_funciones.html",
        funciones=funciones,
        locales=locales,
        local_id=local_id,
        error=error,
    )


SITUACIONES_HISTORIAL = ("Programada", "En curso", "Finalizada", "Cancelada")


@funciones_front_bp.route("/admin/funciones/historial")
@api.admin_front_requerido
def admin_historial_funciones():
    estado, datos = api.pedir("GET", "/api/funciones", params={"incluir_canceladas": "true"})
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion

    funciones = datos.get("funciones", []) if estado == 200 and isinstance(datos, dict) else []
    error = None if estado == 200 else api.mensaje_error(datos)

    for funcion in funciones:
        if funcion.get("estado") == "cancelada":
            funcion["situacion"] = "Cancelada"
        else:
            funcion["situacion"] = _situacion_funcion(funcion)

    filtro = request.args.get("situacion", "")
    if filtro in SITUACIONES_HISTORIAL:
        funciones = [f for f in funciones if f["situacion"] == filtro]
    else:
        filtro = ""

    funciones.sort(key=lambda f: str(f.get("fecha_hora_inicio")), reverse=True)
    return render_template(
        "admin_funciones_historial.html",
        funciones=funciones, error=error, filtro=filtro, situaciones=SITUACIONES_HISTORIAL,
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
            "fecha_hora_inicio": _inicio_funcion(),
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

    estado, respuesta = api.pedir_api(
        "GET", f"/api/funciones/{id_funcion}"
    )
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
    if estado != 200:
        return render_template(
            "admin_funciones.html", funciones=[],
            error=api.mensaje_error(respuesta)
        )
    return redirect(url_for("funciones_front.admin_funciones"))


@funciones_front_bp.route("/admin/funciones/<int:id_funcion>/eliminar", methods=["POST"])
@api.admin_front_requerido
def admin_eliminar_funcion(id_funcion):
    estado, respuesta = api.pedir("DELETE", f"/api/funciones/{id_funcion}")
    redireccion = api.verificar_estado(estado)
    if redireccion:
        return redireccion

    if estado == 200:
        api.flash("La función cancelada se eliminó correctamente", "success")
    else:
        api.flash(api.mensaje_error(respuesta), "error")

    return redirect(url_for("funciones_front.admin_funciones"))