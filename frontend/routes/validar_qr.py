from flask import Blueprint, render_template, request, jsonify
from api import pedir_api, cookies_backend

validar_qr_bp = Blueprint("validar_qr",__name__, url_prefix="/admin")

@validar_qr_bp.route("/validar_qr", methods=["GET", "POST"])
def validar_qr():

    if request.method == "GET":
        return render_template("validar_qr_admin.html")

    token = request.form.get("token", "").strip()
    tipo = request.form.get("tipo", "").strip()
    categoria = request.form.get("categoria", "").strip()

    datos = {
        "token": token
    }
    if tipo == "entrada":

        ruta_backend = "/api/qr/entradas/validar"

    elif tipo == "producto":

        ruta_backend = "/api/qr/productos/validar"
        datos["categoria"] = categoria

    else:

        return jsonify({
            "valido": False,
            "mensaje": "Tipo de QR inválido."
        }), 400

    codigo_http, resultado = pedir_api(
        "POST",
        ruta_backend,
        json=datos,
        cookies=cookies_backend()
    )

    return jsonify(resultado), codigo_http