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
        datos.get("nombre", "").strip(), datos.get("apellido", "").strip(),datos.get("email", "").strip(), datos.get("fecha_nacimiento", "").strip(), datos.get("contrasena", ""))
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
        datos.get("email", "").strip(), datos.get("contrasena", ""))
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

@usuarios_bp.route("/usuarios/me", methods=["PATCH"])
@login_requerido
def editar_perfil():
    datos = request.get_json(silent=True)
    error = usuarios_validator.validar_editar_perfil(datos)
    if error:
        return jsonify(construir_error_api(*error)), 400

    nombre = datos["nombre"].strip() if "nombre" in datos else None
    apellido = datos["apellido"].strip() if "apellido" in datos else None
    email = datos["email"].strip() if "email" in datos else None
    usuario, error = usuarios_service.editar_perfil(session["id_usuario"], nombre, apellido, email)
    if error:
        if error[0] == "SESION_INVALIDA":
            session.clear()
            return jsonify(construir_error_api(*error)), 401 #Unauthorized
        return jsonify(construir_error_api(*error)), 409 #Cualquier otro error, 409 --> conflict
    return jsonify(usuario), 200

@usuarios_bp.route("/usuarios/me", methods=["GET"])
@login_requerido
def ver_perfil():
    usuario, error = usuarios_service.obtener_perfil(session["id_usuario"])
    if error:
        session.clear() #--> El usuario fue dado de baja o desactivado, por lo tanto se cierra su sesion para evitar problemas
        return jsonify(construir_error_api(*error)), 401

    return jsonify(usuario), 200

@usuarios_bp.route("/usuarios/me/password", methods=["PATCH"])
@login_requerido
def cambiar_contrasena():
    datos = request.get_json(silent=True) or {}
    actual = datos.get("contrasena_actual", "")
    nueva = datos.get("nueva_contrasena") or datos.get("contrasena_nueva", "")
    repetir = datos.get("repetir_contrasena")
   
    error = usuarios_validator.validar_contrasena(nueva, repetir)
    if error:
        return jsonify(construir_error_api(*error)), 400
    exito, error = usuarios_service.cambiar_contrasena(session["id_usuario"], actual, nueva)
    if not exito:
        if error[0] == "SESION_INVALIDA":
            session.clear()
            return jsonify(construir_error_api(*error)), 401
        return jsonify(construir_error_api(*error)), 400
    return jsonify({"mensaje": "Contraseña actualizada correctamente"}), 200

@usuarios_bp.route("/usuarios/me/historial", methods=["GET"])
@login_requerido
def ver_historial():
    historial, error = usuarios_service.obtener_historial(session["id_usuario"])
    if error:
        session.clear() 
        return jsonify(construir_error_api(*error)), 401

    return jsonify(historial), 200