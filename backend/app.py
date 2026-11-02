from backend.routes import validar_qr
from dotenv import load_dotenv
import os
from flask import Flask, jsonify
from utils import construir_error_api

load_dotenv()

from flask import Flask
from routes.cancelaciones_routes import cancelaciones_bp






app = Flask(__name__)

app.register_blueprint(cancelaciones_bp)


app.register_blueprint(validar_qr)
app.register_blueprint(salas_bp)






if __name__ == '__main__':
    app.run(debug=True)


app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = os.getenv("SECRET_KEY") #Clave con la que flask firma la cookie de sesion

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")
    
app.register_blueprint(salas_bp)
app.register_blueprint(servicios_bp)
app.register_blueprint(promociones_bp)




app.register_blueprint(locales_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(catalogo_externo_bp)

@app.errorhandler(RuntimeError)
def error_de_conexion(error):
    respuesta = construir_error_api("BASE_DE_DATOS_NO_DISPONIBLE", "Servicio no disponible", str(error))
    return jsonify(respuesta), 503

if __name__ == '__main__':
    app.run(debug=True)