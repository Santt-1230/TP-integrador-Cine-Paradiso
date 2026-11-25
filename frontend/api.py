"""Llamadas del frontend al backend con requests.

Las funciones `get` y `pedir` devuelven siempre (estado, datos).
Si algo falla, `datos` trae {"errors": [{"message": "..."}]} y se lee con mensaje_error().
"""
import os
import requests
from flask import session, redirect, url_for, flash
from functools import wraps


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


def _error(estado, mensaje):
    return estado, {"errors": [{"message": mensaje}]}


def mensaje_error(datos):
    if not isinstance(datos, dict):
        return "Ocurrió un error."

    errores = datos.get("errors")
    if isinstance(errores, list) and errores and isinstance(errores[0], dict):
        error = errores[0]
        return error.get("description") or error.get("message") or error.get("title") or "Error en el servidor."

    for clave in ("mensaje", "message", "description"):
        if datos.get(clave):
            return datos[clave]

    error = datos.get("error")
    if isinstance(error, str):
        return error
    if isinstance(error, dict):
        return error.get("description") or error.get("message") or "Error en el servidor."

    return "Ocurrió un error."


def cookies_backend():
    if "cookie_backend" in session:
        return {"session": session["cookie_backend"]}
    return {}


def pedir(metodo, ruta, datos=None, params=None):
    try:
        r = requests.request(
            metodo, f"{BACKEND_URL}{ruta}",
            json=datos, params=params, cookies=cookies_backend(), timeout=60,
        )
    except requests.RequestException:
        return _error(503, "No se pudo conectar con el servidor. Intenta de nuevo en unos minutos.")

    if "session" in r.cookies:
        session["cookie_backend"] = r.cookies["session"]

    if r.status_code == 204:  # sin cuerpo (por ejemplo, logout)
        return 204, None

    try:
        return r.status_code, r.json()
    except ValueError:
        return _error(502, "El servidor devolvió una respuesta inválida.")


def get(ruta, params=None):
    return pedir("GET", ruta, params=params)


def get_lista(ruta, clave, params=None):
    estado, datos = get(ruta, params)
    if estado != 200:
        return []
    if isinstance(datos, dict):
        datos = datos.get(clave, [])
    return datos if isinstance(datos, list) else []


def pedir_api(metodo, ruta, **opciones):
    try:
        respuesta = requests.request(metodo, BACKEND_URL + ruta, timeout=5, **opciones)
        datos = respuesta.json()
        return respuesta.status_code, datos
    except requests.RequestException:
        return 503, {"errors": [{"message": "No se pudo conectar con el Backend"}]}
    except ValueError:
        return 500, {"errors": [{"message": "El Backend devolvió una respuesta inválida"}]}

def admin_front_requerido(funcion):
    @wraps(funcion)
    def verificar_acceso(*args, **kwargs):

        if not session.get("id_usuario"):
            return redirect(url_for("usuarios.login"))

        if session.get("rol") != "administrador":
            flash('No tienes permiso para acceder a esta página', 'error')
            return redirect(url_for("peliculas_front.inicio"))

        return funcion(*args, **kwargs)

    return verificar_acceso


def limpiar_sesion_front():

    for clave in (
        "id_usuario",
        "nombre",
        "apellido",
        "rol",
        "cookie_backend"
    ):
        session.pop(clave, None)

def redirigir_al_login():
    return redirect(url_for('usuarios.login'))

def redirigir_al_inicio():
    return redirect(url_for('peliculas_front.inicio'))


def verificar_estado(estado):
    if estado == 401:
        limpiar_sesion_front()
        return redirigir_al_login()

    if estado == 403:
        return redirigir_al_inicio()

    return None
