from flask import Blueprint, render_template

estadisticas_bp = Blueprint("estadisticas",__name__, url_prefix="/admin")


@estadisticas_bp.route("/estadisticas")
def estadisticas():
    return render_template("estadisticas_admin.html")