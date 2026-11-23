import logging
from flask import Blueprint, jsonify, request, session
from utils import login_requerido, admin_requerido, construir_error_api, construir_error_db
from validators import opiniones as opiniones_validator
from services import opiniones as opiniones_service

logger = logging.getLogger(__name__)
opiniones_bp = Blueprint('opiniones', __name__, url_prefix='/api')


@opiniones_bp.route('/opiniones', methods=['POST'])
@login_requerido
def crear_opinion():
    datos = request.get_json(silent=True) or {}

    error = opiniones_validator.validar_texto(datos.get("texto"))
    if error:
        return jsonify(construir_error_api(*error)), 400

    puntuacion = datos.get("puntuacion")
    error_punt = opiniones_validator.validar_puntuacion(puntuacion)
    if error_punt:
        return jsonify(construir_error_api(*error_punt)), 400

    categoria_raw = datos.get("categoria")
    categoria = (categoria_raw.strip() or None) if isinstance(categoria_raw, str) else categoria_raw
    error_cat = opiniones_validator.validar_categoria(categoria)
    if error_cat:
        return jsonify(construir_error_api(*error_cat)), 400

    try:
        opiniones_service.crear_opinion(
            session["id_usuario"],
            datos["texto"].strip(),
            puntuacion,
            categoria,
        )
        return jsonify({"mensaje": "Gracias por tu opinión"}), 201
    except Exception:
        logger.exception("Error al guardar la opinión")
        return jsonify(construir_error_db()), 500


@opiniones_bp.route('/opiniones', methods=['GET'])
@login_requerido
@admin_requerido
def listar_opiniones():
    try:
        return jsonify(opiniones_service.listar_opiniones()), 200
    except Exception:
        logger.exception("Error al listar las opiniones")
        return jsonify(construir_error_db()), 500