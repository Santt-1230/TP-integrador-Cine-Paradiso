from flask import Blueprint, render_template

validar_qr_bp = Blueprint("validar_qr",__name__)


@validar_qr_bp.route("/validar-qr")
def validar_qr():
    return render_template("validar_qr.html")