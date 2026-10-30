from flask import Flask
from routes.cancelaciones_routes import cancelaciones_bp

app = Flask(__name__)

app.register_blueprint(cancelaciones_bp)

if __name__ == "__main__":
    app.run(debug=True)