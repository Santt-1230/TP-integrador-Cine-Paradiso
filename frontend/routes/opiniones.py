from flask import Blueprint, flash, redirect, render_template, session, url_for
from api import pedir, mensaje_error, verificar_estado

admin_opiniones_bp = Blueprint('admin_opiniones', __name__)


@admin_opiniones_bp.route('/admin/opiniones')
def admin_opiniones():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    estado, datos = pedir("GET", "/api/opiniones")
    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado != 200:
        flash(mensaje_error(datos), "error")
        datos = []
    return render_template("opiniones.html", opiniones=datos)