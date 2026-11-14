from flask import Blueprint, redirect, render_template, request, url_for

import api

funciones_front_bp = Blueprint("funciones_front", __name__)




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
    estado, datos = api.pedir(
        "GET", "/api/funciones", params={"incluir_canceladas": "true"}
    )
    funciones = datos.get("funciones", []) if estado == 200 else []
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
            "fecha_hora_inicio": request.form.get("fecha_hora_inicio"),
            "precio_entrada": request.form.get("precio_entrada"),
        }
        estado, respuesta = api.pedir(
            "POST", "/api/funciones", datos=datos
        )
        if estado == 201:
            return redirect(url_for("funciones_front.admin_funciones"))
        error = api.mensaje_error(respuesta)

    return render_template(
        "funcion_form.html", funcion=None, error=error
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
        if estado == 200:
            return redirect(url_for("funciones_front.admin_funciones"))
        error = api.mensaje_error(respuesta)

    estado, respuesta = api.pedir_api(
        "GET", f"/api/funciones/{id_funcion}"
    )
    if estado == 200:
        funcion = respuesta.get("funcion")
    elif error is None:
        error = api.mensaje_error(respuesta)

    return render_template(
        "funcion_form.html", funcion=funcion, error=error
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