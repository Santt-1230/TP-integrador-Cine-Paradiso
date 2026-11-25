from datetime import datetime, timedelta
from repositories import estadisticas as estadisticas_repositories
from validators.estadisticas import validar_periodo_estadisticas

def obtener_fecha_inicio(periodo=30):

    if periodo is None:
        periodo = 30

    periodo = validar_periodo_estadisticas(periodo)

    return datetime.now() - timedelta(days=int(periodo))


def obtener_dashboard_estadisticas(periodo=30):

    periodo = validar_periodo_estadisticas(periodo)

    ocupacion_por_funcion = (
        estadisticas_repositories.obtener_ocupacion_por_funcion(
            periodo=periodo)
    )

    capacidad_total = sum(
        int(funcion["capacidad_total"] or 0)
        for funcion in ocupacion_por_funcion)
    
    entradas_ocupadas = sum(
        int(funcion["entradas_ocupadas"] or 0)
        for funcion in ocupacion_por_funcion
    )

    ocupacion_promedio = (
        round(entradas_ocupadas * 100 / capacidad_total, 2)
        if capacidad_total > 0 else 0
    )

    estadisticas = {

        "periodo": periodo,

        "ventas_totales":
            estadisticas_repositories.obtener_ventas_totales(periodo),

        "ventas_entradas":
            estadisticas_repositories.obtener_ventas_entradas(periodo),

        "ventas_productos":
            estadisticas_repositories.obtener_ventas_productos(periodo),

        "cancelaciones":
            estadisticas_repositories.obtener_cancelaciones(periodo),

        "ventas_por_genero":
            estadisticas_repositories.obtener_ventas_por_genero(periodo),

        "entradas_por_franja":
            estadisticas_repositories.obtener_entradas_vendidas_por_franja(
                periodo
            ),

        "ocupacion_por_funcion":
            ocupacion_por_funcion,

        "ocupacion_por_pelicula":
            estadisticas_repositories.obtener_ocupacion_por_pelicula(
                periodo=periodo
            ),

        "ocupacion_promedio":
            ocupacion_promedio
    }

    return estadisticas