from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def admin():
    return render_template("inicio_admin.html")

@admin_bp.route("/usuarios")
def admin_usuarios():
    return render_template("usuarios.html")