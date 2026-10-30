from backend.repositories import estadisticas as estadisticas_repository


def obtener_ventas_totales(periodo):

    if periodo not in ["anual", "mensual", "diario"]:
        return None

    return estadisticas_repository.obtener_ventas_totales(periodo)