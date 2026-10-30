from flask_jwt_extended import JWTManager



def construir_error_api(code:str, message:str, description:str, level:str = 'error')->dict:
    return {
        'errors' :[{
            "error" : level,
            "code" : code,
            "message" : message,
            "description" : description
        }]
    }



jwt = JWTManager()
def init_jwt(app):
    app.config["JWT_SECRET_KEY"] = "tu_clave_secreta"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    jwt.init_app(app)
