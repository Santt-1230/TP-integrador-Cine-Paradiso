from flask import Blueprint, render_template, request
import api


estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/admin")


@estadisticas_bp.route("/estadisticas")
@api.admin_front_requerido
def estadisticas():

    periodo = request.args.get("periodo", "30")

    if periodo not in ("7", "30", "90", "365"):
        periodo = "30"

    # Valores por defecto en caso de error
    datos_vacios = {
        "ocupacion_promedio": 0,
        "ventas_totales": 0,
        "ventas_entradas": 0,
        "ventas_productos": 0,
        "cancelaciones": 0,
        "ventas_por_genero": [],
        "entradas_por_franja": [],
        "ocupacion_por_funcion": [],
        "ocupacion_por_pelicula": []
    }

    # Endpoints de estadísticas
    consultas = {
        "ventas_totales": "/api/estadisticas/ventas_totales",
        "ventas_entradas": "/api/estadisticas/ventas_entradas",
        "ventas_productos": "/api/estadisticas/venta_servicios",
        "cancelaciones": "/api/estadisticas/cancelaciones",
        "ventas_por_genero": "/api/estadisticas/ventas_por_genero",
        "entradas_por_franja": "/api/estadisticas/franjas_horarias",
        "ocupacion_por_funcion": "/api/estadisticas/ocupacion",
        "ocupacion_por_pelicula": "/api/estadisticas/ocupacion/peliculas"
    }

    resultados = {}

    # --------------------------------
    # OBTENER ESTADÍSTICAS
    # --------------------------------

    for clave, ruta in consultas.items():

        estado, datos = api.pedir(
            "GET",
            ruta,
            params={"periodo": periodo}
        )

        # Comprobar errores de autenticación
        redireccion = api.verificar_estado(estado)

        if redireccion:
            return redireccion

        # Comprobar otros errores
        if estado != 200:

            return render_template(
                "estadisticas_admin.html",
                periodo=periodo,
                error=api.mensaje_error(datos),
                **datos_vacios
            )

        resultados[clave] = datos

    # --------------------------------
    # OBTENER RESULTADOS
    # --------------------------------

    ventas_totales = resultados["ventas_totales"]
    ventas_entradas = resultados["ventas_entradas"]
    ventas_productos = resultados["ventas_productos"]
    cancelaciones = resultados["cancelaciones"]

    ventas_por_genero = resultados["ventas_por_genero"]
    entradas_por_franja = resultados["entradas_por_franja"]

    ocupacion_por_funcion = resultados["ocupacion_por_funcion"]
    ocupacion_por_pelicula = resultados["ocupacion_por_pelicula"]

    # Comprobar que los endpoints de listas devuelvan listas
    listas = (
        ventas_por_genero,
        entradas_por_franja,
        ocupacion_por_funcion,
        ocupacion_por_pelicula
    )

    if not all(isinstance(lista, list) for lista in listas):

        return render_template(
            "estadisticas_admin.html",
            periodo=periodo,
            error="El servidor devolvió un formato de estadísticas inválido.",
            **datos_vacios
        )

    # --------------------------------
    # CALCULAR OCUPACIÓN PROMEDIO
    # --------------------------------

    capacidad_total = sum(
        float(funcion.get("capacidad_total") or 0)
        for funcion in ocupacion_por_funcion
    )

    entradas_ocupadas = sum(
        float(funcion.get("entradas_ocupadas") or 0)
        for funcion in ocupacion_por_funcion
    )

    ocupacion_promedio = (
        round(entradas_ocupadas * 100 / capacidad_total, 2)
        if capacidad_total > 0 else 0
    )

    # --------------------------------
    # RENDERIZAR ESTADÍSTICAS
    # --------------------------------

    return render_template(
        "estadisticas_admin.html",

        periodo=periodo,

        ventas_totales=ventas_totales,
        ventas_entradas=ventas_entradas,
        ventas_productos=ventas_productos,
        cancelaciones=cancelaciones,

        ventas_por_genero=ventas_por_genero,
        entradas_por_franja=entradas_por_franja,

        ocupacion_por_funcion=ocupacion_por_funcion,
        ocupacion_por_pelicula=ocupacion_por_pelicula,

        ocupacion_promedio=ocupacion_promedio
    )