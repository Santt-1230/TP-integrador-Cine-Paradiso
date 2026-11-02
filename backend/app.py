import os
from dotenv import load_dotenv

load_dotenv() #Lee el archivo .env y carga las variables

from flask import Flask, jsonify
from routes.salas import salas_bp
from routes.usuarios import usuarios_bp
from routes.funciones import funciones_bp
from utils import construir_error_api


app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = os.getenv("SECRET_KEY") #Clave con la que flask firma la cookie de sesion

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

app.register_blueprint(salas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(funciones_bp)


@app.errorhandler(RuntimeError)
def error_de_conexion(error):
    respuesta = construir_error_api("BASE_DE_DATOS_NO_DISPONIBLE", "Servicio no disponible", str(error))
    return jsonify(respuesta), 503


if __name__ == "__main__":
    app.run(debug=True)
