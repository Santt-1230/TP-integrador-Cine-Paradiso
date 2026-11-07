from flask import Blueprint, render_template

validar_qr_bp = Blueprint("validar_qr",__name__, url_prefix="/admin")


@validar_qr_bp.route("/validar_qr")
def validar_qr():
    return render_template("validar_qr_admin.html")