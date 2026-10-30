import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from routes.usuarios import usuarios_bp
from utils import construir_error_api

load_dotenv() # Lee el archivo .env y carga las variables

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") #Clave con la que flask firma la cookie de sesion

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

app.register_blueprint(usuarios_bp)


@app.errorhandler(ConnectionError)
def error_de_conexion(error):
    respuesta = construir_error_api("BASE_DE_DATOS_NO_DISPONIBLE", "Servicio no disponible", str(error))
    return jsonify(respuesta), 503
