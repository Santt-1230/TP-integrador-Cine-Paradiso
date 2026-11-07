from flask import Blueprint, render_template, redirect, url_for, request, session
import api

servicios_bp = Blueprint("servicios", __name__)

TIPOS = ("comida, bebida, estacionamiento, vip")

def es_admin():
    return session.get("rol") == "administrador"



@servicios_bp.route("/servicios")
def servicios():
    try:
        comidas = api.pedir("GET", "/api/servicios")
    except api.ApiError as e:
        return render_template("servicios.html",)
   