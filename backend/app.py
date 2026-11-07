import os
from dotenv import load_dotenv

load_dotenv() #Lee el archivo .env y carga las variables

from flask import Flask, jsonify

from utils import construir_error_api
from routes.salas import salas_bp
from routes.servicios import servicios_bp
from routes.locales import locales_bp
from routes.usuarios import usuarios_bp
from routes.peliculas import peliculas_bp
from routes.catalogo_externo import catalogo_externo_bp
from routes.cancelaciones import cancelaciones_bp
from routes.admin import admin_bp
from routes.estadisticas import estadisticas_bp
from routes.promociones import promociones_bp
from routes.funciones import funciones_bp

# 1. Cargar variables de entorno
load_dotenv()

# 2. Inicializar la app UNA SOLA VEZ
app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = os.getenv("SECRET_KEY") or "8d9c1ba006f9d7a5c2cc81d83f7a046d332a7fa37e8651c6214b98b4e4d3de7"

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

# 3. Registrar todos los Blueprints
app.register_blueprint(salas_bp)
app.register_blueprint(servicios_bp)
app.register_blueprint(catalogo_externo_bp)
app.register_blueprint(locales_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(cancelaciones_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(promociones_bp)
app.register_blueprint(funciones_bp)

# 4. Manejador global de errores
@app.errorhandler(RuntimeError)
def error_de_conexion(error):
    respuesta = construir_error_api(
        "BASE_DE_DATOS_NO_DISPONIBLE",
        "Servicio no disponible",
        str(error)
    )
    return jsonify(respuesta), 503

if __name__ == "__main__":
    app.run(debug=True, port=5000)
