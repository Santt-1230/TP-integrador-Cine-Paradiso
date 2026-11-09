from datetime import datetime


def validar_id(valor, nombre):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número entero")

    if numero < 1:
        raise ValueError(f"{nombre} debe ser mayor que cero")

    return numero


def validar_fecha_hora(valor):
    if not isinstance(valor, str):
        raise ValueError("fecha_hora_inicio es obligatoria")

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        raise ValueError("fecha_hora_inicio debe tener formato YYYY-MM-DDTHH:MM:SS")


def validar_precio(valor):
    try:
        precio = float(valor)
    except (TypeError, ValueError):
        raise ValueError("precio_entrada debe ser un número")

    if precio < 0:
        raise ValueError("precio_entrada no puede ser negativo")

    return precio


def validar_estado(valor):
    estados = ("programada", "cancelada", "finalizada")
    if valor not in estados:
        raise ValueError("estado debe ser programada, cancelada o finalizada")
    return valor
