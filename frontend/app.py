from routes import admin_bp, estadisticas_bp








app.register_blueprint(admin_bp)
app.register_blueprint(estadisticas_bp)
import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template
from routes.peliculas import peliculas_front_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "desarrollo")
app.register_blueprint(peliculas_front_bp)

@app.route('/mis-compras')
def mis_compras():
    return render_template('mis_compras.html')


if __name__ == "__main__":
    app.run(port=5001, debug=True)
