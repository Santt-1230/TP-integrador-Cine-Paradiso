from flask import Blueprint, request, jsonify, session
from validators import usuarios as usuarios_validator
from services import usuarios as usuarios_service
from utils import login_requerido, construir_error_api

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api")


@usuarios_bp.route("/auth/registro", methods=["POST"])
def registro():
    datos = request.get_json(silent=True)
    error = usuarios_validator.validar_registro(datos)
    if error:
        return jsonify(construir_error_api(*error)), 400
    
    usuario, error = usuarios_service.registrar_usuario(
        datos["nombre"].strip(), datos["apellido"].strip(), datos["email"].strip(), datos["fecha_nacimiento"].strip(), datos["contrasena"])
    if error:
        return jsonify(construir_error_api(*error)), 409

    return jsonify(usuario), 201


@usuarios_bp.route("/auth/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True)
    error = usuarios_validator.validar_login(datos)
    if error: #Valida el formato en el cual el usuario escribio
        return jsonify(construir_error_api(*error)), 400
    
    usuario, error = usuarios_service.autenticar_usuario(
        datos["email"].strip(), datos["contrasena"]
    )
    if error: #Valida los datos contra la base de datos
        return jsonify(construir_error_api(*error)), 401

    session.clear() #Borra cualquier dato de sesion previa antes de inicaiar una nueva
    session["id_usuario"] = usuario["id_usuario"] #Guarda una cookie con el id de la persona autenticad
    session["rol"] = usuario["rol"] 
    return jsonify({"usuario": usuario}), 200

@usuarios_bp.route("/auth/logout", methods=["POST"])
@login_requerido
def logout():
    session.clear()
    return "", 204