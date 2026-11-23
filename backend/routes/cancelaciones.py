from io import BytesIO
import logging
from flask import Blueprint, jsonify, request, send_file, session
from services.cancelaciones import procesar_cancelacion_cliente
from validators.cancelaciones import validar_peticion_cancelacion
from utils import construir_error_api, login_requerido
from services import compras as compras_services
from services import pdf as pdf_services
from services import mailer


logger = logging.getLogger(__name__)
cancelaciones_bp = Blueprint("cancelaciones", __name__, url_prefix="/api")


@cancelaciones_bp.route("/compras/<int:id_compra>", methods=["PATCH"])
@login_requerido
def cancelar_compra_route(id_compra: int):
    datos = request.get_json(silent=True)

    es_valido, mensaje_error = validar_peticion_cancelacion(datos)
    if not es_valido:
        return jsonify({"exito": False, "mensaje": mensaje_error}), 400

    respuesta, status_code = procesar_cancelacion_cliente(
        id_compra, session["id_usuario"], datos
    )

    if status_code == 200:
        try:
            factura, error = compras_services.obtener_factura(id_compra)
            if not error and factura:
                monto = respuesta.get("monto_reembolsado", factura["totales"]["total"])
                pdf_reembolso = pdf_services.generar_pdf_reembolso(factura, monto_reembolso=monto)
                email_cliente = factura["cliente"]["email"]
                numero = factura["factura"].get("numero") or f"compra-{id_compra}"

                adjuntos = [{
                    "contenido": pdf_reembolso,
                    "nombre": f"reembolso-{numero}.pdf",
                    "tipo": "application",
                    "subtipo": "pdf",
                }]

                mailer.enviar_mail(
                    destino=email_cliente,
                    asunto=f"Cancelación y reembolso de compra - {numero}",
                    texto=(
                        f"Hola {factura['cliente']['nombre_pila']}, confirmamos la cancelación de tu compra "
                        f"({numero}). Adjuntamos el comprobante de reembolso por $ {float(monto):.2f}. "
                        "Recordá que las entradas y códigos QR emitidos anteriormente quedaron anulados."
                    ),
                    adjuntos=adjuntos,
                )
        except Exception:
            logger.exception("La compra se canceló, pero falló el envío del mail/PDF de reembolso")

    return jsonify(respuesta), status_code



@cancelaciones_bp.route("/compras/<int:id_compra>/reembolso", methods=["GET"])
@login_requerido
def descargar_reembolso_route(id_compra: int):
    if session.get("rol") == "administrador":
        factura, error = compras_services.obtener_factura(id_compra)
    else:
        factura, error = compras_services.obtener_factura(id_compra, session["id_usuario"])

    if error == "COMPRA_INEXISTENTE" or not factura:
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id_compra} no existe o no le pertenece",
        )), 404

    datos_factura = factura["factura"]
    if datos_factura.get("estado") != "cancelada":
        return jsonify(construir_error_api(
            code="COMPRA_NO_CANCELADA",
            message="COMPRA NO CANCELADA",
            description="Solo las compras canceladas tienen comprobante de reembolso",
        )), 409

    pdf_reembolso = pdf_services.generar_pdf_reembolso(
        factura,
        monto_reembolso=datos_factura.get("monto_reembolsado"),
        fecha_cancelacion=datos_factura.get("fecha_cancelacion"),
    )
    numero = datos_factura.get("numero") or f"compra-{id_compra}"

    return send_file(
        BytesIO(pdf_reembolso),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"reembolso-{numero}.pdf",
    )