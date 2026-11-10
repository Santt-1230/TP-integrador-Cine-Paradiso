from datetime import date, datetime, timedelta

import constants as const
from repositories import funciones as funciones_repository
from validators import funciones as funciones_validator


def serializar_funcion(funcion):
    if funcion is None:
        return None
    for campo in ("fecha_hora_inicio", "fecha_hora_fin"):
        valor = funcion.get(campo)
        if isinstance(valor, datetime):
            funcion[campo] = valor.isoformat(timespec="seconds")
    return funcion


def listar_funciones(filtros, incluir_canceladas=False):
    pelicula_id = filtros.get("pelicula_id")
    local_id = filtros.get("local_id")
    id_sala = filtros.get("id_sala")
    fecha = filtros.get("fecha")

    if pelicula_id not in (None, ""):
        pelicula_id = funciones_validator.validar_id(pelicula_id, "pelicula_id")
    if local_id not in (None, ""):
        local_id = funciones_validator.validar_id(local_id, "local_id")
    if id_sala not in (None, ""):
        id_sala = funciones_validator.validar_id(id_sala, "id_sala")
    if fecha:
        try:
            date.fromisoformat(fecha)
        except ValueError:
            raise ValueError("fecha debe tener formato YYYY-MM-DD")

    funciones = funciones_repository.listar_funciones(
        pelicula_id, local_id, fecha, incluir_canceladas, id_sala
    )
    return [serializar_funcion(funcion) for funcion in funciones]


def obtener_funcion(id_funcion):
    id_funcion = funciones_validator.validar_id(id_funcion, "id_funcion")
    return serializar_funcion(funciones_repository.obtener_funcion(id_funcion))


def obtener_butacas(id_funcion):
    id_funcion = funciones_validator.validar_id(id_funcion, "id_funcion")
    funcion = funciones_repository.obtener_funcion(id_funcion)
    if funcion is None:
        return None
    return funciones_repository.listar_butacas_funcion(id_funcion)


def crear_funcion(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")

    id_pelicula = funciones_validator.validar_id(datos.get("id_pelicula"), "id_pelicula")
    id_sala = funciones_validator.validar_id(datos.get("id_sala"), "id_sala")
    inicio = funciones_validator.validar_fecha_hora(datos.get("fecha_hora_inicio"))
    precio = funciones_validator.validar_precio(datos.get("precio_entrada"))

    if funciones_repository.fecha_hora_pasada(inicio):
        raise ValueError("fecha_hora_inicio debe ser una fecha futura")

    duracion = funciones_repository.obtener_duracion_pelicula(id_pelicula)
    if duracion is None:
        raise ValueError("La película no existe o está inactiva")
    if not funciones_repository.pelicula_vigente_en(id_pelicula, inicio):
        raise ValueError("La película no está en cartelera en la fecha de la función")
    if not funciones_repository.sala_activa(id_sala):
        raise ValueError("La sala no existe o está inactiva")

    fin = inicio + timedelta(minutes=int(duracion))
    if funciones_repository.hay_solapamiento(id_sala, inicio, fin):
        return None, (
            409,
            "HORARIO_NO_DISPONIBLE",
            "Horario no disponible",
            f"La sala necesita al menos {const.MINUTOS_ENTRE_FUNCIONES} minutos libres entre funciones",
        )

    id_funcion = funciones_repository.crear_funcion(
        id_pelicula, id_sala, inicio, fin, precio
    )
    return id_funcion, None


def actualizar_funcion(id_funcion, datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError("Envía al menos un campo en formato JSON")

    id_funcion = funciones_validator.validar_id(id_funcion, "id_funcion")
    actual = funciones_repository.obtener_funcion(id_funcion)
    if actual is None:
        return None, None

    permitidos = {"id_pelicula", "id_sala", "fecha_hora_inicio", "precio_entrada", "estado"}
    if any(campo not in permitidos for campo in datos):
        raise ValueError("Solo se pueden modificar película, sala, inicio, precio o estado")
    if "estado" in datos:
        funciones_validator.validar_estado(datos["estado"])

    solo_cambiar_estado = (
        set(datos) == {"estado"}
        and datos["estado"] in ("cancelada", "finalizada")
    )
    if (
        funciones_repository.funcion_tiene_entradas_activas(id_funcion)
        and not solo_cambiar_estado
    ):
        return None, (
            409,
            "FUNCION_CON_ENTRADAS",
            "No se puede modificar la función",
            "La función tiene entradas reservadas o vendidas. "
            "Cancelala y crea otra función.",
        )

    campos = {}
    id_pelicula = actual["id_pelicula"]
    id_sala = actual["id_sala"]
    inicio = actual["fecha_hora_inicio"]

    if "id_pelicula" in datos:
        id_pelicula = funciones_validator.validar_id(datos["id_pelicula"], "id_pelicula")
        campos["id_pelicula"] = id_pelicula
    if "id_sala" in datos:
        id_sala = funciones_validator.validar_id(datos["id_sala"], "id_sala")
        campos["id_sala"] = id_sala
    if "fecha_hora_inicio" in datos:
        inicio = funciones_validator.validar_fecha_hora(datos["fecha_hora_inicio"])
        campos["fecha_hora_inicio"] = inicio
        if funciones_repository.fecha_hora_pasada(inicio):
            raise ValueError("fecha_hora_inicio debe ser una fecha futura")
    if "precio_entrada" in datos:
        campos["precio_entrada"] = funciones_validator.validar_precio(datos["precio_entrada"])
    if "estado" in datos:
        campos["estado"] = funciones_validator.validar_estado(datos["estado"])

    volver_a_programar = (
        datos.get("estado") == "programada" and actual["estado"] != "programada"
    )
    if (
        "id_pelicula" in datos
        or "id_sala" in datos
        or "fecha_hora_inicio" in datos
        or volver_a_programar
    ):
        duracion = funciones_repository.obtener_duracion_pelicula(id_pelicula)
        if duracion is None:
            raise ValueError("La película no existe o está inactiva")
        if not funciones_repository.pelicula_vigente_en(id_pelicula, inicio):
            raise ValueError("La película no está en cartelera en la fecha de la función")
        if not funciones_repository.sala_activa(id_sala):
            raise ValueError("La sala no existe o está inactiva")

        fin = inicio + timedelta(minutes=int(duracion))
        if funciones_repository.hay_solapamiento(id_sala, inicio, fin, id_funcion):
            return None, (
                409,
                "HORARIO_NO_DISPONIBLE",
                "Horario no disponible",
                f"La sala necesita al menos {const.MINUTOS_ENTRE_FUNCIONES} minutos libres entre funciones",
            )
        campos["fecha_hora_fin"] = fin

    funciones_repository.actualizar_funcion(id_funcion, campos)
    funcion = serializar_funcion(funciones_repository.obtener_funcion(id_funcion))
    return funcion, None


def reservar_butacas(datos, id_usuario):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")

    id_funcion = funciones_validator.validar_id(datos.get("id_funcion"), "id_funcion")
    butacas = datos.get("id_butacas")
    if not isinstance(butacas, list) or not butacas:
        raise ValueError("id_butacas debe ser una lista con al menos una butaca")
    if len(butacas) > 6:
        raise ValueError("No se pueden reservar más de 6 butacas por compra")

    id_butacas = [
        funciones_validator.validar_id(id_butaca, "id_butacas")
        for id_butaca in butacas
    ]
    if len(set(id_butacas)) != len(id_butacas):
        raise ValueError("No se puede repetir una butaca en la misma compra")

    return funciones_repository.reservar_butacas(
        id_usuario, id_funcion, id_butacas
    )
