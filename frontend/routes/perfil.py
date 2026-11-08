from flask import Blueprint, redirect, render_template, session, url_for

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/mi-perfil')

def perfil():
    if not session.get("cookie_back"):
        return redirect(url_for("usuarios.login"))

    r = llamar_back("GET", "/api/<ruta que encuentres>")
    if r.status_code == 401:
        return redirect(url_for("usuarios.login"))

    datos = r.json() if r.ok else {}
    return render_template("perfil.html", perfil=datos)