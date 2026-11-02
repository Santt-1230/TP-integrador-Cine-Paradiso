from flask import render_template

@app.route('/locales', methods = ['GET'])
def mostrar_locales():
    locales = [
        {'id_local':1, 'nombre': 'Cine Centro', 'direccion':''},
        {'id_local':2, 'nombre': 'Cine Norte', 'direccion':''},
        {'id_local':3, 'nombre': 'Cine Sur', 'direccion':''}
    ]
    return render_template('locales.html', locales=locales)
import os
from dotenv import load_dotenv
from flask import Flask, render_template

from routes.admin import admin_bp
from routes.estadisticas import estadisticas_bp
from routes.peliculas import peliculas_front_bp
from routes.usuarios import usuarios_bp
from routes.validar_qr import validar_qr_bp


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

@app.route('/mis-compras')
def mis_compras():
    return render_template('mis_compras.html')


if __name__ == "__main__":
    app.run(port=5001, debug=True)
