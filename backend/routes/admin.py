from flask import Blueprint, jsonify 

admin_bp = Blueprint("bloqueos", __name__)


@admin_bp.route("/api/admin/usuarios", methods=["GET"])
def get_usuarios():
    usuarios = admin_service.obtener_usuarios()
    return jsonify(usuarios), 200

@admin_bp.route("/api/admin/usuarios/<int:id>", methods = ["GET"])
def get_usuario(id):
    pass

@admin_bp.route("/api/admin/usuarios/<int:id>", methods = ["PATCH"])
def update_usuario(id):
    pass

@admin_bp.route("/estadisticas/ocupacion", methods=["GET"])
def get_estadisticas_ocupacion():
    pass

@admin_bp.route("/estadisticas/ventas", methods=["GET"])
def get_estadisticas_ventas():
    pass

@admin_bp.route("/estadisticas/ventas_por_genero", methods=["GET"])
def get_estadisticas_ventas_por_genero():
    pass

@admin_bp.route("/estadisticas/cancelaciones", methods=["GET"])
def get_estadisticas_cancelaciones():
    pass

@admin_bp.route("/estadisticas/franjas_horarias", methods=["GET"]) #horarios que se pasan las peliculas, no los horarios de las funciones
def get_estadisticas_franjas_horarias():
    pass