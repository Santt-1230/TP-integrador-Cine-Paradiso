from datetime import date

import constants as const

FECHAS = ("cartelera_desde", "cartelera_hasta")
CAMPOS_EDITABLES = {"nombre", "sinopsis", "poster_url", "duracion_min", "clasificacion", "activo", *FECHAS}
ESTADOS = ("vigente", "proxima", "vencida", "inactiva")


def parametro_invalido(descripcion):
    return (const.ERROR_CODE_INVALID_PARAMETER, "Parametro invalido", descripcion)


def a_fecha(valor):
    return date.fromisoformat(valor) if isinstance(valor, str) else valor


def _limpiar_campos(datos, permitidos):
    desconocidos = set(datos) - permitidos
    if desconocidos:
        return None, parametro_invalido(f"Campos no permitidos: {', '.join(sorted(desconocidos))}")

    limpio = {}
    for campo, valor in datos.items():
        if campo not in CAMPOS_EDITABLES:
            continue
        if campo == "nombre":
            if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > 255:
                return None, parametro_invalido("El campo 'nombre' debe ser un texto de 1 a 255 caracteres")
            limpio[campo] = valor.strip()
        elif campo == "sinopsis":
            if valor is not None and not isinstance(valor, str):
                return None, parametro_invalido("El campo 'sinopsis' debe ser un texto o null")
            limpio[campo] = valor
        elif campo in ("poster_url", "clasificacion"):
            maximo = 500 if campo == "poster_url" else 20
            if valor is not None and (not isinstance(valor, str) or len(valor) > maximo):
                return None, parametro_invalido(f"El campo '{campo}' debe ser un texto de hasta {maximo} caracteres o null")
            limpio[campo] = valor
        elif campo == "duracion_min":
            if not isinstance(valor, int) or isinstance(valor, bool) or valor < const.ENTERO_POSITIVO_MINIMO:
                return None, parametro_invalido("El campo 'duracion_min' debe ser un numero entero mayor a 0")
            limpio[campo] = valor
        elif campo in FECHAS:
            if valor is not None:
                try:
                    date.fromisoformat(valor)
                except (TypeError, ValueError):
                    return None, parametro_invalido(f"El campo '{campo}' debe tener formato AAAA-MM-DD o ser null")
            limpio[campo] = valor
        elif campo == "activo":
            if not isinstance(valor, bool):
                return None, parametro_invalido("El campo 'activo' debe ser true o false")
            limpio[campo] = int(valor)
    return limpio, None


def validar_edicion(datos):
    if not isinstance(datos, dict) or not datos:
        return None, None, parametro_invalido("Se esperaba un JSON con los campos a modificar")
    limpio, error = _limpiar_campos(datos, CAMPOS_EDITABLES | {"generos"})
    if error:
        return None, None, error
    generos = datos.get("generos")
    if "generos" in datos and (not isinstance(generos, list) or not all(isinstance(g, str) for g in generos)):
        return None, None, parametro_invalido("El campo 'generos' debe ser una lista de nombres de genero")
    return limpio, generos, None


def validar_importacion(datos):
    if not isinstance(datos, dict):
        return None, None, parametro_invalido("Se esperaba un JSON con el campo 'id_externo'")
    id_externo = datos.get("id_externo")
    if isinstance(id_externo, int) and not isinstance(id_externo, bool):
        id_externo = str(id_externo)
    if not isinstance(id_externo, str) or not id_externo.strip().isdigit():
        return None, None, parametro_invalido("El campo 'id_externo' debe ser el ID numerico de TMDB")

    resto = {k: v for k, v in datos.items() if k != "id_externo"}
    opcionales, error = _limpiar_campos(resto, {"duracion_min", "activo", *FECHAS})
    if error:
        return None, None, error
    desde, hasta = a_fecha(opcionales.get("cartelera_desde")), a_fecha(opcionales.get("cartelera_hasta"))
    if desde and hasta and hasta < desde:
        return None, None, parametro_invalido("'cartelera_hasta' no puede ser anterior a 'cartelera_desde'")
    return id_externo.strip(), opcionales, None


def validar_limite(valor):
    try:
        limite = int(valor)
    except (TypeError, ValueError):
        return None, parametro_invalido("El parametro 'limite' debe ser un numero entero")
    return max(const.ENTERO_POSITIVO_MINIMO, min(limite, 50)), None


def validar_estado(estado):
    if estado and estado not in ESTADOS:
        return parametro_invalido(f"El parametro 'estado' debe ser uno de: {', '.join(ESTADOS)}")
    return None


def validar_busqueda_externa(texto, pagina):
    texto = (texto or "").strip()
    if len(texto) < 2:
        return None, None, parametro_invalido("El parametro 'q' debe tener al menos 2 caracteres")
    try:
        pagina = max(const.ENTERO_POSITIVO_MINIMO, int(pagina))
    except (TypeError, ValueError):
        return None, None, parametro_invalido("El parametro 'pagina' debe ser un numero entero")
    return texto, pagina, None
