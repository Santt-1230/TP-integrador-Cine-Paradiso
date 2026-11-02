def validar_periodo_estadisticas(periodo):

    periodos_validos = ("anual", "mensual", "diario")

    if not isinstance(periodo, str):
        raise ValueError("El período debe ser un texto")

    periodo = periodo.strip().lower()

    if periodo not in periodos_validos:
        raise ValueError(
            "El período debe ser anual, mensual o diario"
        )

    return periodo