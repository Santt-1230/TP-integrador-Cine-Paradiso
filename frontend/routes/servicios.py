from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import api

servicios_bp = Blueprint("servicios", __name__)

TIPOS = ("comida", "bebida", "estacionamiento", "vip")

def redirigir_al_login():
    return redirect(url_for("usuarios.login"))


def redirigir_al_inicio():
    return redirect(url_for("peliculas_front.inicio"))


def redirigir_al_listado():
    return redirect(url_for("servicios.admin_servicios"))


def verificar_admin():
    if not session.get("id_usuario"):
        return redirigir_al_login()
    if session.get("rol") != "administrador":
        flash("No tenes permisos para acceder a esta seccion.", "error")
        return redirigir_al_inicio()
    return None


def verificar_estado(estado):
    if estado == 401:
        return redirigir_al_login()
    if estado == 403:
        return redirigir_al_inicio()
    return None


def datos_del_formulario():
    precio = request.form.get("precio", "").strip()
    try:
        precio = float(precio)
    except ValueError:
        pass
    descripcion = request.form.get("descripcion", "").strip()
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "tipo": request.form.get("tipo", ""),
        "descripcion": descripcion or None,
        "precio": precio,
        "activo": "activo" in request.form,
    }


@servicios_bp.route("/servicios")
def servicios():
    estado_productos, productos = api.pedir("GET", "/api/servicios")
    estado_promociones, promociones = api.pedir("GET", "/api/promociones")
    error = None
    if estado_productos != 200:
        error = api.mensaje_error(productos)
        productos = []
    if estado_promociones != 200:
        error = api.mensaje_error(promociones)
        promociones = []
    return render_template("servicios.html", productos=productos, promociones=promociones, error=error)


@servicios_bp.route("/admin/servicios")
def admin_servicios():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("GET", "/api/servicios", params={"incluir_inactivos": "true"})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        return render_template("admin_servicios.html", servicios=[], error=api.mensaje_error(datos_respuesta))
    return render_template("admin_servicios.html", servicios=datos_respuesta)


@servicios_bp.route("/admin/servicios/<int:id_producto>/dar-de-baja", methods=["POST"])
def admin_servicio_dar_de_baja(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("DELETE", f"/api/servicios/{id_producto}")
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/<int:id_producto>/activar", methods=["POST"])
def admin_servicio_activar(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("PATCH", f"/api/servicios/{id_producto}", {"activo": True})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/nuevo", methods=["GET", "POST"])
def admin_servicio_nuevo():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        return render_template("admin_servicio_form.html", servicio={}, tipos=TIPOS)
    datos = datos_del_formulario()
    estado, datos_respuesta = api.pedir("POST", "/api/servicios", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 201:
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/<int:id_producto>/editar", methods=["GET", "POST"])
def admin_servicio_editar(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        estado, datos_respuesta = api.pedir("GET", f"/api/servicios/{id_producto}")
        respuesta = verificar_estado(estado)
        if respuesta:
            return respuesta
        if estado != 200:
            flash(api.mensaje_error(datos_respuesta), "error")
            return redirigir_al_listado()
        return render_template("admin_servicio_form.html", servicio=datos_respuesta, tipos=TIPOS)
    datos = datos_del_formulario()
    estado, datos_respuesta = api.pedir("PATCH", f"/api/servicios/{id_producto}", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        datos["id_producto"] = id_producto
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()