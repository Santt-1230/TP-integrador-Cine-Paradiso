from flask import Blueprint, jsonify,request, session
from validators.validar_qr import validar_token, validar_categoria
from services.validar_qr import procesar_validacion
from utils import admin_requerido

validar_qr_bp = Blueprint('qr_api', __name__, url_prefix='/api/qr')


def validar_qr_por_tipo(tipo: str):

    datos = request.get_json(silent=True)

    if isinstance(datos, dict):

        token = str(datos.get("token") or "").strip()
        categoria = str(datos.get("categoria") or "").strip()
    else:
        token = request.form.get("token", "").strip()
        categoria = request.form.get("categoria", "").strip()

    if not validar_token(token):
        resultado = {
            "valido": False,
            "mensaje": "El token tiene un formato inválido."
        }
        codigo_http = 400
    elif tipo not in ("entrada", "producto"):
        resultado = {
            "valido": False,
            "mensaje": "Tipo de QR inválido."
        }
        codigo_http = 400

    elif tipo == "producto" and not validar_categoria(categoria):

        resultado = {
            "valido": False,
            "mensaje": "La categoría seleccionada no es válida."
        }

        codigo_http = 400

    else:
        try:
            if tipo == "entrada":

                resultado = procesar_validacion(
                    token,
                    session["id_usuario"],
                    "entrada")
            else:
                resultado = procesar_validacion(
                    token,
                    session["id_usuario"],
                    "producto",
                    categoria)

        except Exception:
            resultado = {
                "valido": False,
                "mensaje": "Error al comunicarse con la base de datos."
            }
            codigo_http = 503
        else:
            if resultado["valido"]:
                codigo_http = 200
            elif resultado.get("codigo") == "QR_NO_EXISTE":
                codigo_http = 404
            else:
                codigo_http = 409

    return jsonify(resultado), codigo_http


@validar_qr_bp.route('/entradas/validar', methods=['POST'])
@admin_requerido
def validar_entrada():

    return validar_qr_por_tipo("entrada")


@validar_qr_bp.route('/productos/validar', methods=['POST'])
@admin_requerido
def validar_producto():

    return validar_qr_por_tipo("producto")