from flask import Blueprint, jsonify, request

from services import peliculas as peliculas_service
from utils import admin_requerido, construir_error_api

peliculas_bp = Blueprint("peliculas", __name__, url_prefix="/api")


def _responder(resultado, error, estado_ok=200, clave=None):
    if error:
        estado, code, message, description = error
        return jsonify(construir_error_api(code, message, description)), estado
    return jsonify({clave: resultado} if clave else resultado), estado_ok


@peliculas_bp.get("/peliculas")
def listar_peliculas():
    """Vigentes. Filtros opcionales: ?genero=Accion  ?q=texto"""
    resultado = peliculas_service.listar_vigentes(request.args.get("genero"), request.args.get("q"))
    return jsonify({"peliculas": resultado}), 200


@peliculas_bp.get("/peliculas/<int:id_pelicula>")
def detalle_pelicula(id_pelicula):
    return _responder(*peliculas_service.obtener_publica(id_pelicula))


@peliculas_bp.get("/cartelera")
def cartelera():
    return _responder(*peliculas_service.cartelera(request.args.get("limite", 12)), clave="peliculas")


@peliculas_bp.get("/admin/peliculas")
@admin_requerido
def listar_peliculas_admin():
    return _responder(*peliculas_service.listar_admin(request.args.get("estado"), request.args.get("q")),
                      clave="peliculas")


@peliculas_bp.post("/peliculas")
@admin_requerido
def importar_pelicula():
    return _responder(*peliculas_service.importar(request.get_json(silent=True)), estado_ok=201)


@peliculas_bp.patch("/peliculas/<int:id_pelicula>")
@admin_requerido
def editar_pelicula(id_pelicula):
    return _responder(*peliculas_service.editar(id_pelicula, request.get_json(silent=True)))


@peliculas_bp.delete("/peliculas/<int:id_pelicula>")
@admin_requerido
def dar_de_baja_pelicula(id_pelicula):
    return _responder(*peliculas_service.dar_de_baja(id_pelicula))
