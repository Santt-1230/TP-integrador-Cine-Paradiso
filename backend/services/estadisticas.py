from repositories.estadisticas import (obtener_ventas_totales, 
obtener_ventas_entradas, 
obtener_ventas_productos,
obtener_ventas_por_genero, 
obtener_cancelaciones, obtener_entradas_vendidas_por_franja,
obtener_ocupacion_por_funcion, 
obtener_ocupacion_por_pelicula)
from validators.estadisticas import validar_periodo_estadisticas


def obtener_dashboard_estadisticas(periodo):

    periodo = validar_periodo_estadisticas(periodo)

    ocupacion_por_funcion = obtener_ocupacion_por_funcion(periodo=periodo)
    

    capacidad_total = sum(
        int(funcion["capacidad_total"] or 0)
        for funcion in ocupacion_por_funcion
    )

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
            obtener_ventas_totales(periodo),

        "ventas_entradas":
            obtener_ventas_entradas(periodo),

        "ventas_productos":
            obtener_ventas_productos(periodo),

        "cancelaciones":
            obtener_cancelaciones(periodo),

        "ventas_por_genero":
            obtener_ventas_por_genero(periodo),

        "entradas_por_franja":
            obtener_entradas_vendidas_por_franja(periodo),

        "ocupacion_por_funcion":
            ocupacion_por_funcion,

        "ocupacion_por_pelicula":
            obtener_ocupacion_por_pelicula(
                periodo=periodo
            ),

        "ocupacion_promedio":
            ocupacion_promedio
    }

    return estadisticas