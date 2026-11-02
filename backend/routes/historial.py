import logging
from flask import Blueprint, jsonify, session
from utils import login_requerido, construir_error_db
from services import historial as historial_service

logger = logging.getLogger(__name__)
historial_bp = Blueprint('historial', __name__, url_prefix='/api')


@historial_bp.route('/historial', methods=['GET'])
@login_requerido
def obtener_historial():
    try:
        return jsonify(historial_service.obtener_historial(session["id_usuario"])), 200
    except Exception:
        logger.exception("Error al obtener el historial")
        return jsonify(construir_error_db()), 500