from flask import Blueprint, render_template
from api import ApiError, pedir

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def admin():

    cantidad_peliculas_activas = None
    ocupacion_promedio = None
    cantidad_funciones_programadas = None


    try:
        respuesta = pedir(
            "GET",
            "/api/admin/peliculas/activa"
        )

        cantidad_peliculas_activas = respuesta.get("total", 0)

    except ApiError as error:
        print(f"Error al obtener películas activas: {error.mensaje}")

    # Ocupación promedio
    try:
        ocupacion_por_funcion = pedir(
            "GET",
            "/api/estadisticas/ocupacion",
            params={"periodo": "30"}
        )

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

    except ApiError as error:
        print(f"Error al obtener ocupación: {error.mensaje}")

    try:
        respuesta_funciones = pedir(
            "GET",
            "/api/admin/funciones/programadas"
        )

        cantidad_funciones_programadas = respuesta_funciones.get("total", 0)

    except ApiError as error:
        print(f"Error al obtener las funciones programadas: {error.mensaje}")

    return render_template(
        "inicio_admin.html",
        cantidad_peliculas_activas=cantidad_peliculas_activas,
        ocupacion_promedio=ocupacion_promedio,
        cantidad_funciones_programadas=cantidad_funciones_programadas
    )


@admin_bp.route("/usuarios")
def admin_usuarios():
    return render_template("usuarios.html")