from flask import Blueprint, jsonify, request

from services import catalogo_externo as catalogo_service
from utils import admin_requerido, construir_error_api

catalogo_externo_bp = Blueprint("catalogo_externo", __name__, url_prefix="/api/catalogo-externo")


@catalogo_externo_bp.get("/peliculas")
@admin_requerido
def buscar_en_tmdb():
    """?q=texto (minimo 2 letras)  &pagina=N (opcional)."""
    resultado, error = catalogo_service.buscar(request.args.get("q"), request.args.get("pagina", 1))
    if error:
        estado, code, message, description = error
        return jsonify(construir_error_api(code, message, description)), estado
    return jsonify(resultado), 200
