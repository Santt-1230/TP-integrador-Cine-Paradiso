"""Llamadas del frontend al backend con requests.

Las funciones `get` y `pedir` devuelven siempre (estado, datos).
Si algo falla, `datos` trae {"errors": [{"message": "..."}]} y se lee con mensaje_error().
"""
import os
import requests
from flask import session,redirect, url_for
from functools import wraps


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


def _error(estado, mensaje):
    """Arma un error con el mismo formato que usa el backend."""
    return estado, {"errors": [{"message": mensaje}]}


def mensaje_error(datos):
    """Devuelve un texto legible a partir del cuerpo de error del backend, venga como venga."""
    if not isinstance(datos, dict):
        return "Ocurrió un error."

    # El backend manda los errores como una lista: {"errors": [{...}]}
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
    """Cookie de sesión del backend, guardada en la sesión del frontend al hacer login."""
    if "cookie_backend" in session:
        return {"session": session["cookie_backend"]}
    return {}


def pedir(metodo, ruta, datos=None, params=None):
    """Hace la llamada al backend y devuelve (estado, cuerpo).

    Reenvía la cookie de sesión y guarda la nueva si el backend manda una (login).
    Si no hay conexión o la respuesta no es JSON, devuelve (503/502, error).
    """
    try:
        r = requests.request(
            metodo, f"{BACKEND_URL}{ruta}",
            json=datos, params=params, cookies=cookies_backend(), timeout=10,
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

    if "session" in r.cookies:
        session["cookie_backend"] = r.cookies["session"]

    if r.status_code == 204:  # sin cuerpo (por ejemplo, logout)
        return 204, None

    try:
        return r.status_code, r.json()
    except ValueError:
        return _error(502, "El servidor devolvió una respuesta inválida.")

    try:
        datos = respuesta.json()
    except ValueError:
        return f"El servidor devolvió una respuesta inválida (HTTP {respuesta.status_code})."

    if not isinstance(datos, dict):
        return f"El servidor respondió con un error HTTP {respuesta.status_code}."

    # Formato con lista de errores
    errores = datos.get("errors")

    if isinstance(errores, list) and errores:
        error = errores[0]

        if isinstance(error, dict):
            return (
                error.get("description")
                or error.get("message")
                or error.get("title")
                or "Error en el servidor."
            )

    # Otros formatos posibles
    for clave in ("mensaje", "message", "description"):
        if datos.get(clave):
            return datos[clave]

    error = datos.get("error")

    if isinstance(error, str):
        return error

    if isinstance(error, dict):
        return (
            error.get("description")
            or error.get("message")
            or "Error en el servidor."
        )

    return f"El servidor respondió con un error HTTP {respuesta.status_code}."

def get(ruta, params=None):
    """GET al backend. Devuelve (estado, cuerpo)."""
    return pedir("GET", ruta, params=params)


def get_lista(ruta, clave, params=None):
    """Devuelve la lista que viene en el campo `clave`. Si falla o no hay nada, devuelve []."""
    estado, datos = get(ruta, params)
    if estado != 200:
        return []
    if isinstance(datos, dict):
        datos = datos.get(clave, [])
    return datos if isinstance(datos, list) else []


def pedir_api(metodo, ruta, **opciones):
    """Llamada simple al backend: acepta cualquier opción de requests (json, params, cookies...).

    Devuelve (estado, datos). No reenvía la sesión por sí sola.
    """
    try:
        respuesta = requests.request(metodo, BACKEND_URL + ruta, timeout=5, **opciones)
        datos = respuesta.json()
        return respuesta.status_code, datos
    except requests.RequestException:
        return 503, {"errors": [{"message": "No se pudo conectar con el Backend"}]}
    except ValueError:
<<<<<<< HEAD
        return 500, {"errors": [{"message": "El Backend devolvió una respuesta inválida"}]}
=======
        return 500, {"errors": [{"message": "El Backend devolvió una respuesta inválida"}]}

def admin_front_requerido(funcion):
    @wraps(funcion)
    def verificar_acceso(*args, **kwargs):

        if not session.get("id_usuario"):
            return redirect(url_for("usuarios.login"))

        if session.get("rol") != "administrador":
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
>>>>>>> origin/feature/front-js-estilizacion
