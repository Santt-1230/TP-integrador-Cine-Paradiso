from flask import Blueprint, request, jsonify, session, current_app

from services.validar_qr import (
    procesar_validacion_entrada,
    procesar_validacion_producto
)

from validators.validar_qr import (
    validar_token,
    validar_categoria
)

from utils import admin_requerido


validar_qr = Blueprint(
    "validar_qr",
    __name__,
    url_prefix="/api/qr"
)


# ====================================
# OBTENER DATOS DEL QR
# ====================================

def obtener_datos_qr():

    datos = request.get_json(silent=True)

    if isinstance(datos, dict):

        token = str(datos.get("token") or "").strip()
        categoria = str(datos.get("categoria") or "").strip()

    else:

        token = request.form.get("token", "").strip()
        categoria = request.form.get("categoria", "").strip()

    return token, categoria


# ====================================
# PROCESAR VALIDACIÓN SEGÚN TIPO
# ====================================

def validar_qr_por_tipo(tipo):

    token, categoria = obtener_datos_qr()

    # --------------------------------
    # VALIDAR FORMATO DEL TOKEN
    # --------------------------------

    if not validar_token(token):

        return jsonify({
            "valido": False,
            "mensaje": "El token tiene un formato inválido."
        }), 400

    # --------------------------------
    # OBTENER USUARIO VALIDADOR
    # --------------------------------

    id_validador = session.get("id_usuario")

    if id_validador is None:

        return jsonify({
            "valido": False,
            "mensaje": "Debe iniciar sesión."
        }), 401

    # --------------------------------
    # VALIDAR ENTRADA
    # --------------------------------

    if tipo == "entrada":

        try:

            resultado = procesar_validacion_entrada(
                token,
                id_validador
            )

        except Exception:

            current_app.logger.exception(
                "Error al validar el QR de entrada."
            )

            return jsonify({
                "valido": False,
                "mensaje": "Error al comunicarse con la base de datos."
            }), 503

    # --------------------------------
    # VALIDAR PRODUCTO
    # --------------------------------

    elif tipo == "producto":

        if not validar_categoria(categoria):

            return jsonify({
                "valido": False,
                "mensaje": "La categoría seleccionada no es válida."
            }), 400

        try:

            resultado = procesar_validacion_producto(
                token,
                id_validador,
                categoria
            )

        except Exception:

            current_app.logger.exception(
                "Error al validar el QR de producto."
            )

            return jsonify({
                "valido": False,
                "mensaje": "Error al comunicarse con la base de datos."
            }), 503

    else:

        return jsonify({
            "valido": False,
            "mensaje": "Tipo de QR inválido."
        }), 400

    # --------------------------------
    # DETERMINAR RESPUESTA HTTP
    # --------------------------------

    if resultado["valido"]:

        codigo_http = 200

    elif (
        resultado.get("codigo") == "QR_NO_EXISTE"
        or resultado.get("mensaje") == "El QR no existe"
    ):

        codigo_http = 404

    else:

        codigo_http = 409

    return jsonify(resultado), codigo_http


# ====================================
# VALIDAR ENTRADA
# ====================================

@validar_qr.route("/entradas/validar", methods=["POST"])
@admin_requerido
def validar_entrada():

    return validar_qr_por_tipo("entrada")


# ====================================
# VALIDAR PRODUCTO
# ====================================

@validar_qr.route("/productos/validar", methods=["POST"])
@admin_requerido
def validar_producto():

    return validar_qr_por_tipo("producto")