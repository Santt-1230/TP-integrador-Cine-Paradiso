from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from routes.salas import salas_bp
from routes.locales import locales_bp
from db import obtener_conexion

app = Flask(__name__)

app.json.ensure_ascii = False

app.register_blueprint(salas_bp)
app.register_blueprint(locales_bp)





if __name__ == '__main__':
    app.run(debug=True)