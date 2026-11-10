from flask import Blueprint, render_template, redirect, url_for, request, session
import api

servicios_bp = Blueprint("servicios", __name__)

TIPOS = ("comida", "bebida", "estacionamiento", "vip")


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
    try:
        productos = api.pedir("GET", "/api/servicios")
        promociones = api.pedir("GET", "/api/promociones")
    except api.ApiError as e:
        return render_template("servicios.html", productos=[], promociones=[], error=e.mensaje)
    return render_template("servicios.html", productos=productos, promociones=promociones)


@servicios_bp.route("/admin/servicios")
def admin_servicios():
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    try:
        lista = api.pedir("GET", "/api/servicios?incluir_inactivos=true")
    except api.ApiError as e:
        return render_template("admin_servicios.html", servicios=[], error=e.mensaje)
    return render_template("admin_servicios.html", servicios=lista)


@servicios_bp.route("/admin/servicios/<int:id_producto>/dar-de-baja", methods=["POST"])
def admin_servicio_dar_de_baja(id_producto):
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    try:
        api.pedir("DELETE", f"/api/servicios/{id_producto}")
    except api.ApiError as e:
        print("ERROR DAR DE BAJA:", e.estado, e.mensaje)
        lista = api.pedir("GET", "/api/servicios?incluir_inactivos=true")
        return render_template("admin_servicios.html", servicios=lista, error=e.mensaje)
    return redirect(url_for("servicios.admin_servicios"))


@servicios_bp.route("/admin/servicios/<int:id_producto>/activar", methods=["POST"])
def admin_servicio_activar(id_producto):
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    try:
        api.pedir("PATCH", f"/api/servicios/{id_producto}", {"activo": True})
    except api.ApiError:
        pass
    return redirect(url_for("servicios.admin_servicios"))


@servicios_bp.route("/admin/servicios/nuevo", methods=["GET", "POST"])
def admin_servicio_nuevo():
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    if request.method == 'GET':
        return render_template("admin_servicio_form.html", servicio={}, tipos=TIPOS)
    datos = datos_del_formulario()
    try:
        api.pedir("POST", "/api/servicios", datos)
    except api.ApiError as e:
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS, error=e.mensaje)
    return redirect(url_for("servicios.admin_servicios"))


@servicios_bp.route("/admin/servicios/<int:id_producto>/editar", methods=["GET", "POST"])
def admin_servicio_editar(id_producto):
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    if request.method == "GET":
        try:
            servicio = api.pedir("GET", f"/api/servicios/{id_producto}")
        except api.ApiError:
            return redirect(url_for("servicios.admin_servicios"))
        return render_template("admin_servicio_form.html", servicio=servicio, tipos=TIPOS)
    datos = datos_del_formulario()
    try:
        api.pedir("PATCH", f"/api/servicios/{id_producto}", datos)
    except api.ApiError as e:
        datos["id_producto"] = id_producto
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS, error=e.mensaje)
    return redirect(url_for("servicios.admin_servicios"))
