from flask import (Blueprint,render_template,request,session,redirect,url_for)
import api


estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/admin")


@estadisticas_bp.route("/estadisticas")
def estadisticas():

    # Verificar que exista una sesión
    if not session.get("id_usuario"):
        return redirect(url_for("usuarios.login"))

    # Verificar que sea administrador
    if session.get("rol") != "administrador":
        return redirect(url_for("peliculas_front.inicio"))

    # Obtener período seleccionado
    periodo = request.args.get("periodo", "30")

    if periodo not in ("7", "30", "90", "365"):
        periodo = "30"

    try:

        # VENTAS TOTALES
        ventas_totales = api.pedir(
            "GET",
            "/api/estadisticas/ventas_totales",
            params={"periodo": periodo}
        )

        # ENTRADAS VENDIDAS
        ventas_entradas = api.pedir(
            "GET",
            "/api/estadisticas/ventas_entradas",
            params={"periodo": periodo}
        )

        # VENTAS DE PRODUCTOS
        ventas_productos = api.pedir(
            "GET",
            "/api/estadisticas/venta_servicios",
            params={"periodo": periodo}
        )

        # CANCELACIONES
        cancelaciones = api.pedir(
            "GET",
            "/api/estadisticas/cancelaciones",
            params={"periodo": periodo}
        )

        # VENTAS POR GÉNERO
        ventas_por_genero = api.pedir(
            "GET",
            "/api/estadisticas/ventas_por_genero",
            params={"periodo": periodo}
        )

        # ENTRADAS POR FRANJA HORARIA
        entradas_por_franja = api.pedir(
            "GET",
            "/api/estadisticas/franjas_horarias",
            params={"periodo": periodo}
        )

        # OCUPACIÓN POR FUNCIÓN
        ocupacion_por_funcion = api.pedir(
            "GET",
            "/api/estadisticas/ocupacion",
            params={"periodo": periodo}
        )

        # OCUPACIÓN POR PELÍCULA
        ocupacion_por_pelicula = api.pedir(
            "GET",
            "/api/estadisticas/ocupacion/peliculas",
            params={"periodo": periodo}
        )

    except api.ApiError as error:

        # Si el backend ya no reconoce la sesión,
        # volvemos a solicitar el inicio de sesión.
        if error.estado == 401:
            for clave in (
                "id_usuario",
                "nombre",
                "apellido",
                "rol",
                "cookie_backend"
            ):
                session.pop(clave, None)

            return redirect(url_for("usuarios.login"))

        return render_template(
            "estadisticas_admin.html",
            periodo=periodo,
            error=error.mensaje,
            ocupacion_promedio=0,
            ventas_totales=0,
            ventas_entradas=0,
            ventas_productos=0,
            cancelaciones=0,
            ventas_por_genero=[],
            entradas_por_franja=[],
            ocupacion_por_funcion=[],
            ocupacion_por_pelicula=[]
        )

    # CALCULAR OCUPACIÓN PROMEDIO

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

    # ENVIAR INFORMACIÓN A LA PLANTILLA

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