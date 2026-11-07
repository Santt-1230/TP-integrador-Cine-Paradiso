"""Llamadas del Frontend al Backend (requests). Un solo lugar para la URL, el timeout y los errores."""
import os
import requests
from flask import session

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


class ApiError(Exception):
    def __init__(self, estado, mensaje):
        super().__init__(mensaje)
        self.estado = estado
        self.mensaje = mensaje

def _mensaje(respuesta):
    try:
        errores = respuesta.json().get("errors") or []
        if errores:
            return errores[0].get("description") or errores[0].get("message")
    except (ValueError, AttributeError):
        pass
    return "El servidor respondio con un error."


def get(ruta, params=None):
    try:
        r = requests.get(f"{BACKEND_URL}{ruta}", params=params, timeout=10)
    except requests.RequestException:
        raise ApiError(503, "No se pudo conectar con el servidor. Intenta de nuevo en unos minutos.")
    if not r.ok:
        raise ApiError(404 if r.status_code == 404 else 502, _mensaje(r))
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


def pedir(metodo, ruta, datos=None):
    try:
        r = requests.request(metodo, f"{BACKEND_URL}{ruta}", json=datos, cookies=cookies_backend(), timeout=10) #Si no hay conexion o se agota el tiempo de espera
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
