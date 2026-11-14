def validar_periodo_estadisticas(periodo):

    periodos_validos = ("7", "30", "90", "365")

    if not isinstance(periodo, (str, int)):
        raise ValueError("El período debe ser válido")

    periodo = str(periodo).strip()

    if periodo not in periodos_validos:
        raise ValueError("El período debe ser 7, 30, 90 o 365 días")

    return periodo