"""Funciones sencillas para llamar al Backend desde Python con requests."""
import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


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
