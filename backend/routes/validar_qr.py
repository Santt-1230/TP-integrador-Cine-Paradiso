from flask import Blueprint, request, jsonify, session

from services.validar_qr import procesar_validacion_qr
from validators.validar_qr import validar_token
from utils import requiere_admin


validar_qr = Blueprint('validar_qr', __name__, url_prefix='/api/qr')


def validar_qr_por_tipo(tipo):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "mensaje": "Debe proporcionar los datos"
        }), 400

    token = datos.get("token")

    if not validar_token(token):
        return jsonify({
            "mensaje": "El token tiene un formato inválido"
        }), 400

    id_validador = session.get("id_usuario")

    if id_validador is None:
        return jsonify({
            "mensaje": "Debe iniciar sesión"
        }), 401

    try:

        resultado = procesar_validacion_qr(
            token,
            id_validador,
            tipo
        )

        if resultado["valido"]:
            return jsonify(resultado), 200

        if resultado.get("codigo") == "QR_NO_EXISTE":
            return jsonify(resultado), 404

        return jsonify(resultado), 409

    except RuntimeError:

        return jsonify({
            "mensaje": "Error al comunicarse con la base de datos"
        }), 503


@validar_qr.route('/entradas/validar', methods=['PATCH'])
@requiere_admin
def validar_entrada():

    return validar_qr_por_tipo("entrada")


@validar_qr.route('/productos/validar', methods=['PATCH'])
@requiere_admin
def validar_producto():

    return validar_qr_por_tipo("producto")