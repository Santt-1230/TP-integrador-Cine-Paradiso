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

