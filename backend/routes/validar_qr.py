from flask import Blueprint,request, jsonify, session
from services.validar_qr import procesar_validacion_qr
from validators.validar_qr import validar_token
from utils import admin_requerido

from services.validar_qr import (procesar_validacion_entrada, procesar_validacion_producto)
from validators.validar_qr import (validar_token, validar_categoria)
from utils import admin_requerido

validar_qr_bp = Blueprint(
    'qr_api',
    __name__,
    url_prefix='/api/qr'
)


def _validar_qr_por_tipo(tipo: str):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "valido": False,
            "mensaje": "Debe proporcionar los datos."
        }), 400

    token = datos.get("token")

    if not validar_token(token):
        return jsonify({
            "valido": False,
            "mensaje": "El token tiene un formato inválido."
        }), 400

    id_validador = session.get("id_usuario")

    try:

        if tipo == "entrada":

            resultado = procesar_validacion_entrada(
                token,
                id_validador
            )

        elif tipo == "producto":

            categoria = datos.get("categoria")

            if not validar_categoria(categoria):
                return jsonify({
                    "valido": False,
                    "mensaje": "La categoría seleccionada no es válida."
                }), 400

            resultado = procesar_validacion_producto(
                token,
                id_validador,
                categoria
            )

        else:
            return jsonify({
                "valido": False,
                "mensaje": "Tipo de QR inválido."
            }), 400

        if resultado["valido"]:
            return jsonify(resultado), 200

        if resultado.get("codigo") == "QR_NO_EXISTE":
            return jsonify(resultado), 404

        return jsonify(resultado), 409

    except RuntimeError:
        return jsonify({
            "valido": False,
            "mensaje": "Error al comunicarse con la base de datos."
        }), 503


@validar_qr_bp.route('/entradas/validar', methods=['PATCH'])
@admin_requerido
def validar_entrada():

    return _validar_qr_por_tipo("entrada")


@validar_qr_bp.route('/productos/validar', methods=['PATCH'])
@admin_requerido
def validar_producto():

    return _validar_qr_por_tipo("producto")