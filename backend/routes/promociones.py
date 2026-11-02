from flask import Blueprint, jsonify
from backend.services.promociones import listar_promociones

promociones_bp = Blueprint('promociones', __name__, url_prefix='/api')

@promociones_bp.route('/promociones', methods=['GET'])
def obtener_promociones_route():
    promociones = listar_promociones()
    return jsonify(promociones), 200
