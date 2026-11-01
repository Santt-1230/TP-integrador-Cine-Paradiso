import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from backend.routes.usuarios import usuarios_bp
from backend.routes.compras import compras_bp
from backend.routes.admin import admin_bp
from backend.utils import construir_error_api

load_dotenv() # Lee el archivo .env y carga las variables

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") #Clave con la que flask firma la cookie de sesion
app.json.ensure_ascii = False

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

app.register_blueprint(usuarios_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(admin_bp)


@app.errorhandler(ConnectionError)
def error_de_conexion(error):
    respuesta = construir_error_api("BASE_DE_DATOS_NO_DISPONIBLE", "Servicio no disponible", str(error))
    return jsonify(respuesta), 503
if __name__ == '__main__':
    app.run(debug=True)
