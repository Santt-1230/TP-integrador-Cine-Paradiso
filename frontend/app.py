import os

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for


load_dotenv()

app = Flask(__name__)
API_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


def pedir_api(metodo, ruta, **opciones):
    try:
        respuesta = requests.request(
            metodo, API_URL + ruta, timeout=5, **opciones
        )
        return respuesta.status_code, respuesta.json()
    except requests.RequestException:
        return 503, {"errors": [{"message": "No se pudo conectar con el backend"}]}
    except ValueError:
        return 500, {"errors": [{"message": "El backend devolvió una respuesta inválida"}]}


def mensaje_error(datos):
    errores = datos.get("errors", [])
    if errores:
        return errores[0].get("description") or errores[0].get("message")
    return datos.get("message", "Ocurrió un error")


@app.route("/")
def inicio():
    return redirect(url_for("pagina_funciones"))


@app.route("/funciones")
def pagina_funciones():
    estado, datos = pedir_api("GET", "/api/funciones", params=request.args)
    funciones = datos.get("funciones", []) if estado == 200 else []
    error = None if estado == 200 else mensaje_error(datos)
    return render_template(
        "funciones.html", funciones=funciones, filtros=request.args, error=error,
        locales=[],
    )


@app.route("/funciones/<int:id_funcion>/butacas")
def pagina_butacas(id_funcion):
    estado, datos = pedir_api("GET", f"/api/funciones/{id_funcion}/butacas")
    butacas = datos.get("butacas", []) if estado == 200 else []
    error = None if estado == 200 else mensaje_error(datos)
    return render_template(
        "funcion_butacas.html", id_funcion=id_funcion, butacas=butacas,
        error=error, locales=[],
    ), estado if estado >= 500 else 200


@app.route("/admin/funciones")
def admin_funciones():
    estado, datos = pedir_api(
        "GET", "/api/funciones", params={"incluir_canceladas": "true"}
    )
    funciones = datos.get("funciones", []) if estado == 200 else []
    error = None if estado == 200 else mensaje_error(datos)
    return render_template(
        "admin_funciones.html", funciones=funciones, error=error, locales=[]
    )


@app.route("/admin/funciones/nueva", methods=["GET", "POST"])
def admin_nueva_funcion():
    error = None
    if request.method == "POST":
        datos = {
            "id_pelicula": request.form.get("id_pelicula"),
            "id_sala": request.form.get("id_sala"),
            "fecha_hora_inicio": request.form.get("fecha_hora_inicio"),
            "precio_entrada": request.form.get("precio_entrada"),
        }
        estado, respuesta = pedir_api("POST", "/api/funciones", json=datos)
        if estado == 201:
            return redirect(url_for("admin_funciones"))
        error = mensaje_error(respuesta)

    return render_template("funcion_form.html", funcion=None, error=error, locales=[])


@app.route("/admin/funciones/<int:id_funcion>/editar", methods=["GET", "POST"])
def admin_editar_funcion(id_funcion):
    error = None
    funcion = None

    if request.method == "POST":
        datos = {}
        for campo in ("id_pelicula", "id_sala", "fecha_hora_inicio", "precio_entrada"):
            valor = request.form.get(campo)
            if valor:
                datos[campo] = valor
        estado, respuesta = pedir_api(
            "PATCH", f"/api/funciones/{id_funcion}", json=datos
        )
        if estado == 200:
            return redirect(url_for("admin_funciones"))
        error = mensaje_error(respuesta)

    estado, respuesta = pedir_api("GET", f"/api/funciones/{id_funcion}")
    if estado == 200:
        funcion = respuesta.get("funcion")
    elif error is None:
        error = mensaje_error(respuesta)

    return render_template("funcion_form.html", funcion=funcion, error=error, locales=[])


@app.route("/admin/funciones/<int:id_funcion>/cancelar", methods=["POST"])
def admin_cancelar_funcion(id_funcion):
    estado, respuesta = pedir_api(
        "PATCH", f"/api/funciones/{id_funcion}", json={"estado": "cancelada"}
    )
    if estado != 200:
        return render_template(
            "admin_funciones.html", funciones=[], error=mensaje_error(respuesta), locales=[]
        )
    return redirect(url_for("admin_funciones"))


if __name__ == "__main__":
    app.run(port=5001, debug=True)
