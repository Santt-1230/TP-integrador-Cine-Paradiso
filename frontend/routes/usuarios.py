from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, session

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["id_usuario"] = 1
        return redirect(url_for("usuarios.mi_cuenta"))
    return render_template("login.html")

@usuarios_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        session["id_usuario"] = 1
        return redirect(url_for("usuarios.mi_cuenta"))
    hoy = date.today().isoformat()
    return render_template("registro.html", fecha_maxima=hoy)

@usuarios_bp.route("/mi-cuenta", methods=["GET", "POST"])
def mi_cuenta():
    if not session.get("id_usuario"):
        return redirect(url_for("usuarios.login"))
    return render_template("mi_cuenta.html")

@usuarios_bp.route("/mi-cuenta/correo", methods=["POST"])
def cambiar_correo():
    return redirect(url_for("usuarios.mi_cuenta"))

@usuarios_bp.route("/mi-cuenta/password", methods=["POST"])
def cambiar_contrasena():
    return redirect(url_for("usuarios.mi_cuenta"))

@usuarios_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("usuarios.login"))