import os
from dotenv import load_dotenv
from flask import Flask, render_template

from routes.admin import admin_bp
from routes.estadisticas import estadisticas_bp
from routes.peliculas import peliculas_front_bp
from routes.usuarios import usuarios_bp
from routes.validar_qr import validar_qr_bp
from routes.locales import locales_bp
from routes.perfil import perfil_bp
from routes.servicios import servicios_bp
from routes.funciones import funciones_front_bp
from routes.salas import salas_bp
from routes.compras import compras_bp
from routes.admin_peliculas import admin_peliculas_bp
from routes.opiniones import admin_opiniones_bp
...
load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "desarrollo")

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

# Registrar todos los blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(peliculas_front_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(validar_qr_bp)
app.register_blueprint(locales_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(funciones_front_bp)
app.register_blueprint(salas_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(servicios_bp)
app.register_blueprint(admin_peliculas_bp)
app.register_blueprint(admin_opiniones_bp)


if __name__ == "__main__":
    app.run(port=5001, debug=True)