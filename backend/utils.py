from flask import jsonify
from flask_jwt_extended import JWTManager
from functools import wraps


def construir_error_api(code:str, message:str, description:str, level:str = 'error')->dict:
    return {
        'errors' :[{
            "error" : level,
            "code" : code,
            "message" : message,
            "description" : description
        }]
    }



def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        claims = get_jwt()

        if claims.get("rol") != "admin":
            return jsonify({
                "error": "No tenés permisos de administrador"
            }), 403

        return func(*args, **kwargs)

    return wrapper


jwt = JWTManager()
def init_jwt(app):
    app.config["JWT_SECRET_KEY"] = "tu_clave_secreta"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    jwt.init_app(app)