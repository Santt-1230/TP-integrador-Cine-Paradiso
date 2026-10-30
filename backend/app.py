from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from routes.salas import salas_bp
from routes.admin import admin_bp

import os

app = Flask(__name__)

app.json.ensure_ascii = False

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.register_blueprint(salas_bp)
app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)