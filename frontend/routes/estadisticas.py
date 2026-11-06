from flask import Blueprint, render_template

estadisticas_bp = Blueprint("estadisticas",__name__)


@estadisticas_bp.route("/estadisticas")
def estadisticas():
    return render_template("estadisticas.html")