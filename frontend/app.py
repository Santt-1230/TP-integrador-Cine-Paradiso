import os
from flask import Flask, render_template

from dotenv import load_dotenv

from routes.admin import admin_bp
from routes.estadisticas import estadisticas_bp
from routes.peliculas import peliculas_front_bp
from routes.validar_qr import validar_qr_bp








load_dotenv()




app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "desarrollo")


app.register_blueprint(peliculas_front_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(estadisticas_bp)



@app.route('/mis-compras')
def mis_compras():
    return render_template('mis_compras.html')


if __name__ == "__main__":
    app.run(port=5001, debug=True)
