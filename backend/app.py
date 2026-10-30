from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from routes.salas import salas_bp
from routes.admin import admin_bp
from routes.compras import compras_bp
from utils import init_jwt

app = Flask(__name__)

app.json.ensure_ascii = False

init_jwt(app)

app.register_blueprint(salas_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(compras_bp)


if __name__ == '__main__':
    app.run(debug=True)