from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from api import ApiError, pedir, admin_front_requerido, limpiar_sesion_front

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")



@admin_bp.route("/")
def admin():
    cantidad_peliculas_activas = None
    ocupacion_promedio = None
    cantidad_funciones_programadas = None

    try:
        respuesta = pedir( "GET","/api/admin/peliculas/activa")
        cantidad_peliculas_activas = respuesta.get("total", 0)

    except ApiError as error:
        print(f"Error al obtener películas activas: {error.mensaje}")

    try:
        ocupacion_por_funcion = pedir("GET","/api/estadisticas/ocupacion", params={"periodo": "30"})

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
        respuesta_funciones = pedir("GET","/api/admin/funciones/programadas")
        cantidad_funciones_programadas = respuesta_funciones.get("total", 0)

    except ApiError as error:
        print(f"Error al obtener las funciones programadas: {error.mensaje}")

    return render_template(
        "inicio_admin.html",
        cantidad_peliculas_activas=cantidad_peliculas_activas,
        ocupacion_promedio=ocupacion_promedio,
        cantidad_funciones_programadas=cantidad_funciones_programadas
        )

@admin_bp.route("/usuarios", methods=["GET"])
@admin_front_requerido
def admin_usuarios():

    buscar = request.args.get("buscar", "").strip()
    editar_id = request.args.get("editar", type=int)
    usuario_editar = None
    error = None

    try:
        usuarios = pedir("GET","/api/admin/usuarios")

    except ApiError as e:

        if e.estado == 401:
            limpiar_sesion_front()
            return redirect(url_for("usuarios.login"))

        if e.estado == 403:
            flash(e.mensaje, "error")
            return redirect(url_for("peliculas_front.inicio"))

        usuarios = []
        error = e.mensaje

    if buscar:

        termino = buscar.casefold()

        usuarios = [
            usuario for usuario in usuarios
            if termino in (usuario.get("nombre") or "").casefold()
            or termino in (usuario.get("email") or "").casefold()
            or termino in (usuario.get("rol") or "").casefold()
        ]

    if editar_id is not None:

        print("ID RECIBIDO:", editar_id)

        try:

            usuario_editar = pedir(
                "GET",
                f"/api/admin/usuarios/{editar_id}/editar"
            )

            print("USUARIO OBTENIDO:", usuario_editar)

        except ApiError as e:

            print("ERROR:", e.estado, e.mensaje)

            if e.estado == 401:
                limpiar_sesion_front()
                return redirect(url_for("usuarios.login"))

            if e.estado == 403:
                flash(e.mensaje, "error")
                return redirect(url_for("peliculas_front.inicio"))

            flash(e.mensaje, "error")

            
    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        buscar=buscar,
        usuario_editar=usuario_editar,
        cantidad_usuarios=len(usuarios),
        error=error
    )


@admin_bp.route("/usuarios/<int:id>/editar", methods=["POST"])
@admin_front_requerido
def actualizar_usuario_front(id):

    buscar = request.form.get("buscar", "").strip()

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "email": request.form.get("email", "").strip(),
        "rol": request.form.get("rol", "").strip()
    }

    try:

        pedir(
            "PATCH",
            f"/api/admin/usuarios/{id}/editar",
            datos=datos
        )

        flash("Usuario actualizado correctamente.", "success")

    except ApiError as e:

        if e.estado == 401:
            limpiar_sesion_front()
            return redirect(url_for("usuarios.login"))

        if e.estado == 403:
            flash(e.mensaje, "error")
            return redirect(url_for("peliculas.inicio"))

        flash(e.mensaje, "error")

        return redirect(
            url_for(
                "admin.admin_usuarios",
                editar=id,
                buscar=buscar
            )
        )

    return redirect(
        url_for(
            "admin.admin_usuarios",
            buscar=buscar
        )
    )