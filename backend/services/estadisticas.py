from repositories import estadisticas as estadisticas_repository
from validators.estadisticas import validar_periodo_estadisticas
from repositories.estadisticas import (
    obtener_ventas_totales,
    obtener_ventas_entradas,
    obtener_ventas_productos,
    obtener_ventas_por_genero,
    obtener_cancelaciones,
    obtener_entradas_vendidas_por_franja,
    obtener_ocupacion_por_funcion,
    obtener_ocupacion_por_pelicula
)

from validators.estadisticas import (
    validar_periodo_estadisticas
)


def obtener_dashboard_estadisticas(periodo):

    periodo = validar_periodo_estadisticas(periodo)

    estadisticas = {
        "ventas_totales": obtener_ventas_totales(periodo),

        "ventas_entradas": obtener_ventas_entradas(),

        "ventas_productos": obtener_ventas_productos(),

        "ventas_por_genero": obtener_ventas_por_genero(),

        "cancelaciones": obtener_cancelaciones(),

        "entradas_por_franja": obtener_entradas_vendidas_por_franja(),

        "ocupacion_por_funcion": obtener_ocupacion_por_funcion(),

        "ocupacion_por_pelicula": obtener_ocupacion_por_pelicula()
    }

    return estadisticas