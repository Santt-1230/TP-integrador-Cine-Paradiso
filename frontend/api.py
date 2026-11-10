"""Llamadas del Frontend al Backend (requests). Un solo lugar para la URL, el timeout y los errores."""
import os
import requests
from flask import session, url_for, redirect
from functools import wraps

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


class ApiError(Exception):
    def __init__(self, estado, mensaje):
        super().__init__(mensaje)
        self.estado = estado
        self.mensaje = mensaje

def _mensaje(respuesta):

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
    try:
        r = requests.get(f"{BACKEND_URL}{ruta}", params=params, timeout=10)
    except requests.RequestException:
        raise ApiError(503, "No se pudo conectar con el servidor. Intenta de nuevo en unos minutos.")
    if not r.ok:
        raise ApiError(r.status_code, _mensaje(r))
    try:
        return r.json()
    except ValueError:
        raise ApiError(502, "El servidor devolvio una respuesta invalida.")


def get_lista(ruta, clave, params=None):
    try:
        datos = get(ruta, params)
    except ApiError:
        return []
    if isinstance(datos, dict):
        datos = datos.get(clave, [])
    return datos if isinstance(datos, list) else []



def cookies_backend():
    if "cookie_backend" in session: # La cookie de sesión del back se guarda dentro de la session del front
        return {"session": session["cookie_backend"]}
    return {}


def pedir(metodo, ruta, datos=None,params=None):
    try:
        r = requests.request(metodo, f"{BACKEND_URL}{ruta}", json=datos, params=params, cookies=cookies_backend(), timeout=10) #Si no hay conexion o se agota el tiempo de espera
    except requests.RequestException:
        raise ApiError(503, "No se pudo conectar con el servidor. Intenta de nuevo en unos minutos.")

    if "session" in r.cookies: #El back mandó cookie (login)
        session["cookie_backend"] = r.cookies["session"]

    if not r.ok:
        raise ApiError(r.status_code, _mensaje(r))
    if r.status_code == 204: #None ya que el 204 (logout) no devuelve cuerpo
        return None
    try:
        return r.json()
    except ValueError:
        raise ApiError(502, "El servidor devolvio una respuesta invalida.")


def pedir_api(metodo, ruta, **opciones):
    try:
        respuesta = requests.request(
            metodo, BACKEND_URL + ruta, timeout=5, **opciones
        )
        datos = respuesta.json()
        return respuesta.status_code, datos
    except requests.RequestException:
        return 503, {"errors": [{"message": "No se pudo conectar con el Backend"}]}
    except ValueError:
        return 500, {"errors": [{"message": "El Backend devolvió una respuesta inválida"}]}


def mensaje_error(datos):
    errores = datos.get("errors", [])
    if errores:
        return errores[0].get("description") or errores[0].get("message")
    return datos.get("message", "Ocurrió un error")



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