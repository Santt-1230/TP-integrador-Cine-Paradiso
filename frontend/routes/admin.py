from flask import Blueprint, render_template
from api import ApiError, pedir

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def admin():
        cantidad_peliculas_activas = None
        try:
            respuesta = pedir("GET", "/api/admin/peliculas/activa")
            cantidad_peliculas_activas = respuesta.get("total", 0)
        
        except ApiError as error:
            print(f"Error al obtener películas activas: {error.mensaje}")

        return render_template("inicio_admin.html", cantidad_peliculas_activas=cantidad_peliculas_activas)



@admin_bp.route("/usuarios")
def admin_usuarios():
    return render_template("usuarios.html")