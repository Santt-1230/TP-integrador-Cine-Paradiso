from flask import Blueprint, render_template, request
import api


estadisticas_bp = Blueprint("estadisticas",__name__,url_prefix="/admin")


@estadisticas_bp.route("/estadisticas")
@api.admin_front_requerido
def estadisticas():

    periodo = request.args.get("periodo", "30")

    if periodo not in ("7", "30", "90", "365"):
        periodo = "30"

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

    estado, datos = api.pedir("GET", "/api/estadisticas/dashboard", params={"periodo": periodo})

    redireccion = api.verificar_estado(estado)

    if redireccion:
        return redireccion

    if estado != 200:
        return render_template(
            "estadisticas_admin.html",
            periodo=periodo,
            error=api.mensaje_error(datos),
            **datos_vacios
        )

    listas = (
        "ventas_por_genero",
        "entradas_por_franja",
        "ocupacion_por_funcion",
        "ocupacion_por_pelicula"
    )

    if not isinstance(datos, dict) or not all(
        isinstance(datos.get(clave), list)
        for clave in listas
    ):
        return render_template(
            "estadisticas_admin.html",
            periodo=periodo,
            error="El servidor devolvió un formato de estadísticas inválido.",
            **datos_vacios
        )

    datos.pop("periodo", None)

    return render_template(
        "estadisticas_admin.html",
        periodo=periodo,
        **datos
    )