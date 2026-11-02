import os
from dotenv import load_dotenv
from datetime import date

load_dotenv() #Lee el archivo .env y carga las variables

from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") 

if not app.secret_key:
    raise RuntimeError("Falta la SECRET_KEY en el .env")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    hoy = date.today().isoformat()
    return render_template("registro.html", fecha_maxima=hoy)

@app.route("/mi-cuenta", methods=["GET", "POST"])
def mi_cuenta():
    if not session.get("id_usuario"):
        return redirect(url_for("login"))
    return render_template("mi_cuenta.html")

@app.route("/mi-cuenta/correo", methods=["POST"])
def cambiar_correo():
    return redirect(url_for("mi_cuenta"))

@app.route("/mi-cuenta/password", methods=["POST"])
def cambiar_contrasena():
    return redirect(url_for("mi_cuenta"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)