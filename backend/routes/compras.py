from flask import Blueprint, jsonify, session, request, send_file
from io import BytesIO
from utils import construir_error_api, validar_entero_positivo,login_requerido
from services import compras as compras_services
from services import pdf as pdf_services
from validators import compras as compras_validators
from services import mailer
compras_bp = Blueprint('compras', __name__, url_prefix='/api')
def usuario_registrado():
    return {'id': 1, 'acceso': "admin"}

@compras_bp.route('/compras', methods=['GET'])
@login_requerido
def listar_compras():
    id_usuario = session["id_usuario"]
    compras, error = compras_services.listar_compras(id_usuario)
 
    if error == "SIN_COMPRAS":
        return jsonify(construir_error_api(
            code="SIN_COMPRAS",
            message="Usuario sin compras",
            description=f"La compra del usuario de ID: {id_usuario} no existe o no le pertenece"
        )), 404
    return jsonify(compras), 200




@compras_bp.route('/compras/<int:id>', methods=['GET'])
@login_requerido
def compra_id(id):
    if session["rol"] == "administrador":
        compra, error = compras_services.compra_id(id)
    else:
        compra, error = compras_services.compra_id(id, session["id_usuario"])
    if error == "COMPRA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id} no existe o no le pertenece"
        )), 404
    return jsonify(compra), 200



@compras_bp.route('/compras', methods=['POST'])
@login_requerido
def registrar_compras():
    datos = request.get_json()
    id_compra,error = compras_services.registrar_compra(session["id_usuario"], datos)
    if error == "FUNCION_INEXISTENTE":
        return jsonify(construir_error_api(
            code="FUNCION_INEXISTENTE",
            message="Funcion no encontrada",
            description=f"La funcion de ID: {datos["id_funcion"]} no existe"
        )), 404
    if error == "FUNCION_NO_DISPONIBLE":
        return jsonify(construir_error_api(
            code="FUNCION_NO_DISPONIBLE",
            message="Funcion no disponible",
            description=f"La funcion de ID: {datos["id_funcion"]} no se encuentra disponible"
        )), 400
    if error == "ERROR_COMPRA":
        return jsonify(construir_error_api(
            code="ERROR_COMPRA",
            message="ERROR AL REGISTRAR UNA COMPRA",
            description="No se pudo registrar"
        )), 500
    if error == "BUTACA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="BUTACA_INEXISTENTE",
            message="Butaca inexistente",
            description="Alguna butaca no existe o no pertenece a la sala de esta funcion"
        )), 404
    if error == "BUTACA_INACTIVA":
        return jsonify(construir_error_api(
            code="BUTACA_INACTIVA",
            message="Butaca inactiva",
            description="Alguna butaca seleccionada está inactiva. Volvé al mapa y elegí otras.",
        )), 409
    if error == "BUTACA_NO_DISPONIBLE":
        return jsonify(construir_error_api(
            code="BUTACA_NO_DISPONIBLE",
            message="Butaca no disponible",
            description="Algunas de las butacas no esta disponible"
        )), 409
    if error == "PRODUCTO_NO_DISPONIBLE":
        return jsonify(construir_error_api(
            code=error,
            message="Producto no disponible",
            description="Uno de los productos no existe o está inactivo",
        )), 404
    if error == "PROMOCION_NO_DISPONIBLE":
        return jsonify(construir_error_api(
            code=error,
            message="Promoción no disponible",
            description="La promoción seleccionada no está vigente o ya no es válida para entradas. Actualizá el checkout e intentá de nuevo.",
        )), 409
    if error is not None:
        return jsonify(error), 400

    factura, error = compras_services.obtener_factura(id_compra)
    pdf = pdf_services.generar_pdf_factura(factura)
    email_cliente = factura["cliente"]["email"]
    numero = factura["factura"].get("numero") or f"compra-{id_compra}"
    qrs, error_qr = compras_services.obtener_qr(id_compra, session["id_usuario"])
    adjuntos = [{
        "contenido": pdf,
        "nombre": f"factura-{numero}.pdf",
        "tipo": "application",
        "subtipo": "pdf",
    }]
    if not error_qr:
        adjuntos.append({
            "contenido": pdf_services.generar_pdf_entradas(factura, qrs),
            "nombre": f"entradas-{numero}.pdf",
            "tipo": "application",
            "subtipo": "pdf",
        })
    mailer.enviar_mail(
        destino=email_cliente,
        asunto="Factura de compra - Cine Paradiso",
        texto="¡Gracias por tu compra! Adjuntamos tu factura y tus entradas con códigos QR.",
        adjuntos=adjuntos,
    )
    return jsonify({"message": "Compra registrada"}), 201
    
@compras_bp.route('/compras/<int:id>/cancelacion', methods=['PATCH'])
@login_requerido
def cancelar_compra(id):
    error = compras_services.cancelar_compra(id, session["id_usuario"])
 
    if error == "COMPRA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id} no existe o no le pertenece"
        )), 404
    if error == "ERROR_CANCELACION":
        return jsonify(construir_error_api(
            code="ERROR_CANCELACION",
            message="CANCELACION RECHAZADA",
            description=f"No se pudo cancelar la compra con ID: {id}"
        )), 409
    return jsonify({"message": "Compra cancelada con exito"}), 200

    




@compras_bp.route('/compras/<int:id>/factura', methods=['GET'])
@login_requerido
def obtener_factura(id):
    if session["rol"] == "administrador":
        factura, error = compras_services.obtener_factura(id)
    else:
        factura, error = compras_services.obtener_factura(id, session["id_usuario"])
 
    if error == "COMPRA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id} no existe o no le pertenece"
        )), 404
    pdf = pdf_services.generar_pdf_factura(factura)
    numero = factura["factura"].get("numero") or f"compra-{id}"
    nombre_archivo = f"factura-{numero}.pdf"
    return send_file(
        BytesIO(pdf), mimetype="application/pdf", as_attachment=True,
        download_name=nombre_archivo,
    )




@compras_bp.route('/compras/<int:id>/qr', methods=['GET'])
@login_requerido
def obtener_qr(id):
    id_usuario = session["id_usuario"]
    rol = session["rol"]
    if rol == "administrador":
        qrs, error = compras_services.obtener_qr(id)
    else:
        qrs, error = compras_services.obtener_qr(id, id_usuario)

    if error == "COMPRA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id} no existe o no le pertenece"
        )), 404
    if error == "COMPRA_NO_CONFIRMADA":
        return jsonify(construir_error_api(
            code="COMPRA_NO_CONFIRMADA",
            message="COMPRA NO CONFIRMADA",
            description="Solo las compras confirmadas tienen QR"
        )), 409
    if error == "ENTRADAS_SIN_CONFIRMAR":
        return jsonify(construir_error_api(
            code="ENTRADAS_SIN_CONFIRMAR",
            message="Ninguna entrada confirmada",
            description="No tiene ninguna compra comfirmada"
        )), 409
    if error == "ERROR_GENERAR_QR":
        return jsonify(construir_error_api(
            code="ERROR_GENERAR_QR",
            message="No se pudieron generar los QR",
            description="No se pudo crear un QR para cada entrada confirmada"
        )), 500
    factura, error_factura = compras_services.obtener_factura(
        id, None if rol == "administrador" else id_usuario
    )
    if error_factura == "COMPRA_INEXISTENTE":
        return jsonify(construir_error_api(
            code="COMPRA_INEXISTENTE",
            message="COMPRA NO ENCONTRADA",
            description=f"La compra de ID: {id} no existe o no le pertenece"
        )), 404
    pdf = pdf_services.generar_pdf_entradas(factura, qrs)
    numero = factura["factura"].get("numero") or f"compra-{id}"
    return send_file(
        BytesIO(pdf), mimetype="application/pdf", as_attachment=True,
        download_name=f"entradas-{numero}.pdf",
    )