from flask import Flask
from routes.cancelaciones_routes import cancelaciones_bp

app = Flask(__name__)

app.register_blueprint(cancelaciones_bp)

if __name__ == "__main__":
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from routes.salas import salas_bp
from db import obtener_conexion

app = Flask(__name__)

app.json.ensure_ascii = False

app.register_blueprint(salas_bp)






if __name__ == '__main__':
    app.run(debug=True)