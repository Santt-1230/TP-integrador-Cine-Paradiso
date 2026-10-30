from flask import Blueprint, jsonify 

estadisticas_bp = Blueprint("estadisticas", __name__)

@estadisticas_bp.route("/estadisticas/ocupacion", methods=["GET"])
def get_estadisticas_ocupacion():
    pass

@estadisticas_bp.route("/estadisticas/ventas", methods=["GET"])
def get_estadisticas_ventas():
    pass

@estadisticas_bp.route("/estadisticas/ventas_por_genero", methods=["GET"])
def get_estadisticas_ventas_por_genero():
    pass

@estadisticas_bp.route("/estadisticas/cancelaciones", methods=["GET"])
def get_estadisticas_cancelaciones():
    pass

@estadisticas_bp.route("/estadisticas/franjas_horarias", methods=["GET"]) #horarios que se pasan las peliculas, no los horarios de las funciones
def get_estadisticas_franjas_horarias():
    pass