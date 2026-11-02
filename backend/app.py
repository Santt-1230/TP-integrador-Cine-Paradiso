import os
from dotenv import load_dotenv
from flask import Flask, jsonify

from routes.salas import salas_bp
from routes.admin import admin_bp
from routes.usuarios import usuarios_bp
from routes.estadisticas import estadisticas_bp

from utils import construir_error_api

load_dotenv()

app = Flask(__name__)

app.json.ensure_ascii = False
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")


app.register_blueprint(salas_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(estadisticas_bp)


@app.errorhandler(ConnectionError)
def error_de_conexion(error):
    respuesta = construir_error_api(
        "BASE_DE_DATOS_NO_DISPONIBLE",
        "Servicio no disponible",
        str(error)
    )
    return jsonify(respuesta), 503


if __name__ == "__main__":
    app.run(debug=True)