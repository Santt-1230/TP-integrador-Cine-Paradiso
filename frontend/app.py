import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from routes.peliculas import peliculas_front_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "desarrollo")
app.register_blueprint(peliculas_front_bp)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
