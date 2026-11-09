from flask import Blueprint, jsonify,request, session, current_app
from validators.validar_qr import validar_token, validar_categoria
from services.validar_qr import procesar_validacion_entrada, procesar_validacion_producto
from utils import admin_requerido

validar_qr_bp = Blueprint('qr_api', __name__, url_prefix='/api/qr')



def validar_qr_por_tipo(tipo: str):

    token = request.form.get("token", "").strip()
    categoria = request.form.get("categoria", "").strip()

    # Validar formato del token.
    if not validar_token(token):

        resultado = {
            "valido": False,
            "mensaje": "El token tiene un formato inválido."
        }

        codigo_http = 400

    # Validar entrada.
    elif tipo == "entrada":

        try:

            resultado = procesar_validacion_entrada(
                token,
                session["id_usuario"]
            )

        except Exception:

            current_app.logger.exception(
                "Error al validar el QR de entrada."
            )

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

    # Validar producto.
    elif tipo == "producto":

        if not validar_categoria(categoria):

            resultado = {
                "valido": False,
                "mensaje": "La categoría seleccionada no es válida."
            }

            codigo_http = 400

        else:

            try:

                resultado = procesar_validacion_producto(
                    token,
                    session["id_usuario"],
                    categoria
                )

            except Exception:

                current_app.logger.exception(
                    "Error al validar el QR de producto."
                )

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

    else:

        resultado = {
            "valido": False,
            "mensaje": "Tipo de QR inválido."
        }

        codigo_http = 400

    return jsonify(resultado), codigo_http




@validar_qr_bp.route('/entradas/validar', methods=['PATCH'])
@admin_requerido
def validar_entrada():

    return validar_qr_por_tipo("entrada")


@validar_qr_bp.route('/productos/validar', methods=['PATCH'])
@admin_requerido
def validar_producto():

    return validar_qr_por_tipo("producto")