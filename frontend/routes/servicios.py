from flask import Blueprint, render_template, redirect, url_for, request, session
import api

servicios_bp = Blueprint("servicios", __name__)

TIPOS = ("comida, bebida, estacionamiento, vip")


@servicios_bp.route("/servicios")
def servicios():
    try:
        todos = api.pedir("GET", "/api/servicios")
        promociones = api.pedir("GET", "/api/promociones")
    except api.ApiError as e:
        return render_template("servicios.html", comidas=[], promociones=[], error=e.mensaje)
    comidas = []
    for servicio in todos:
        if servicio["tipo"] in ("comida", "bebida"):
            comidas.append(servicio)

    return render_template("servicios.html", comidas=comidas, promociones=promociones)


@servicios_bp.route("/admin/servicios")
def admin_servicios():
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    try:
        lista = api.pedir("GET", "/api/servicios?incluir_inactivos=true")
    except api.ApiError as e:
        return render_template("admin_servicios.html", servicios=[], error=e.mensaje)
    return render_template("admin_servicios.html", servicios=lista)


@servicios_bp.route("/admin/servicios/<int:id_producto>/dar-de-baja", methods=['POST'])
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


@servicios_bp.route("/admin/servicios/<int:id_producto>/activar", methods=['POST'])
def admin_servicio_activar(id_producto):
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))
    try:
        api.pedir("PATCH", f"/api/servicios/{id_producto}", {"activo": True})
    except api.ApiError:
        pass
    return redirect(url_for("servicios.admin_servicios"))
