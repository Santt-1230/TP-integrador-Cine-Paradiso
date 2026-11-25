from datetime import date, datetime
from flask import Blueprint, render_template, url_for, flash, request, redirect
from api import (verificar_estado,pedir,mensaje_error, admin_front_requerido)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


TEXTO_ESTADO = {"vigente": "Vigente", "proxima": "Próxima"}


def convertir_fecha(texto):
    if not texto:
        return None

    try:
        return datetime.fromisoformat(
            str(texto).strip().replace(" ", "T")
        ).replace(tzinfo=None)

    except (TypeError, ValueError):
        return None


def fecha_ar(texto):
    fecha = convertir_fecha(texto)

    return fecha.strftime("%d/%m/%Y") if fecha else "—"



def resumen_funciones():

    estado, datos = pedir("GET","/api/funciones",params={"incluir_canceladas": "true"})
    
    if estado != 200 or not isinstance(datos, dict):
        return {}, {}
    
    funciones = datos.get("funciones", [])

    if not isinstance(funciones, list):
        return {}, {}

    ahora = datetime.now()

    proximas = {}
    cantidades = {}

    for funcion in funciones:

        if funcion.get("estado") == "programada":

            inicio = convertir_fecha(funcion.get("fecha_hora_inicio"))
            fin = convertir_fecha(funcion.get("fecha_hora_fin"))

            if fin and fin > ahora:

                id_pelicula = funcion.get("id_pelicula")

                cantidades[id_pelicula] = cantidades.get(id_pelicula, 0) + 1

                if inicio:

                    cine = funcion.get("local")
                    sufijo = " · " + cine if cine else ""

                    if inicio <= ahora:
                        orden = (0, inicio)
                        descripcion = "En curso (hasta " + fin.strftime("%H:%M") + ")" + sufijo

                    else:
                        orden = (1, inicio)
                        descripcion = inicio.strftime("%d/%m %H:%M") + sufijo

                    proximas.setdefault(id_pelicula, []).append(
                        (orden, descripcion)
                    )

    proximas_ordenadas = {}

    for id_pelicula, elementos in proximas.items():

        elementos.sort(key=lambda elemento: elemento[0])

        proximas_ordenadas[id_pelicula] = [
            descripcion for orden, descripcion in elementos
        ]

    return proximas_ordenadas, cantidades

def novedades_inicio():

    estado, respuesta = pedir("GET", "/api/admin/peliculas")

    if estado != 200 or not isinstance(respuesta, dict):
        print("Error al obtener las películas:", mensaje_error(respuesta))
        return []

    peliculas = [
        p for p in respuesta.get("peliculas", [])
        if p.get("estado_cartelera") in TEXTO_ESTADO
    ]

    peliculas.sort(
        key=lambda p: (
            p["estado_cartelera"] != "vigente",
            p.get("cartelera_desde") or "")
    )
    proximas, cantidades = resumen_funciones()

    return [
        {
            "nombre": p.get("nombre"),
            "poster_url": p.get("poster_url"),
            "fecha_estreno": fecha_ar(p.get("cartelera_desde")),
            "cantidad_funciones": cantidades.get(p.get("id_pelicula"), 0),
            "proxima_funcion": proximas.get(p.get("id_pelicula"), []),
            "estado": TEXTO_ESTADO[p["estado_cartelera"]],
        }
        for p in peliculas[:10]
    ]


@admin_bp.route("/")
@admin_front_requerido
def admin():

    cantidad_peliculas_activas = None
    ocupacion_promedio = None
    cantidad_funciones_programadas = None

    # --------------------------------
    # PELICULAS ACTIVAS
    # --------------------------------

    estado, respuesta = pedir("GET","/api/admin/peliculas/activa")

    redireccion = verificar_estado(estado)

    if redireccion:
        return redireccion

    if estado == 200 and isinstance(respuesta, dict):

        cantidad_peliculas_activas = respuesta.get("total", 0)

    else:
        print(
            "Error al obtener películas activas:",
            mensaje_error(respuesta)
        )

    # --------------------------------
    # OCUPACION PROMEDIO
    # --------------------------------

    estado, ocupacion_por_funcion = pedir("GET","/api/estadisticas/ocupacion",params={"periodo": "30"})

    redireccion = verificar_estado(estado)

    if redireccion:
        return redireccion

    if estado == 200 and isinstance(ocupacion_por_funcion, list):

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

    else:
        print(
            "Error al obtener ocupación:",
            mensaje_error(ocupacion_por_funcion)
        )

    # --------------------------------
    # FUNCIONES PROGRAMADAS
    # --------------------------------

    estado, respuesta_funciones = pedir(
        "GET",
        "/api/admin/funciones/programadas"
    )

    redireccion = verificar_estado(estado)

    if redireccion:
        return redireccion

    if estado == 200 and isinstance(respuesta_funciones, dict):

        cantidad_funciones_programadas = respuesta_funciones.get("total", 0)

    else:
        print(
            "Error al obtener las funciones programadas:",
            mensaje_error(respuesta_funciones)
        )

    novedades = novedades_inicio()

    return render_template(
        "inicio_admin.html",
        cantidad_peliculas_activas=cantidad_peliculas_activas,
        ocupacion_promedio=ocupacion_promedio,
        cantidad_funciones_programadas=cantidad_funciones_programadas,
        novedades=novedades
    )


# ====================================
# ADMINISTRACIÓN DE USUARIOS
# ====================================

@admin_bp.route("/usuarios", methods=["GET"])
@admin_front_requerido
def admin_usuarios():

    buscar = request.args.get("buscar", "").strip()
    editar_id = request.args.get("editar", type=int)

    usuario_editar = None
    error = None

    # --------------------------------
    # OBTENER USUARIOS
    # --------------------------------

    estado, usuarios = pedir(
        "GET",
        "/api/admin/usuarios"
    )

    redireccion = verificar_estado(estado)

    if redireccion:
        return redireccion

    if estado != 200:

        error = mensaje_error(usuarios)
        usuarios = []

    elif not isinstance(usuarios, list):

        error = "El servidor devolvió un formato de usuarios inválido."
        usuarios = []

    # --------------------------------
    # FILTRAR USUARIOS
    # --------------------------------

    if buscar:

        termino = buscar.casefold()

        usuarios = [
            usuario for usuario in usuarios
            if termino in (usuario.get("nombre") or "").casefold()
            or termino in (usuario.get("email") or "").casefold()
            or termino in (usuario.get("rol") or "").casefold()
        ]

    # --------------------------------
    # OBTENER USUARIO PARA EDITAR
    # --------------------------------

    if editar_id is not None:

        estado, usuario_editar = pedir(
            "GET",
            f"/api/admin/usuarios/{editar_id}/editar"
        )

        redireccion = verificar_estado(estado)

        if redireccion:
            return redireccion

        if estado != 200:

            print(
                "ERROR:",
                estado,
                mensaje_error(usuario_editar)
            )

            flash(mensaje_error(usuario_editar), "error")
            usuario_editar = None


    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        buscar=buscar,
        usuario_editar=usuario_editar,
        cantidad_usuarios=len(usuarios),
        error=error
    )


# ====================================
# ACTUALIZAR USUARIO
# ====================================

@admin_bp.route("/usuarios/<int:id>/editar", methods=["POST"])
@admin_front_requerido
def actualizar_usuario_front(id):

    buscar = request.form.get("buscar", "").strip()

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "email": request.form.get("email", "").strip(),
        "rol": request.form.get("rol", "").strip()
    }

    estado, respuesta = pedir(
        "PATCH",
        f"/api/admin/usuarios/{id}/editar",
        datos=datos
    )

    redireccion = verificar_estado(estado)

    if redireccion:
        return redireccion

    if 200 <= estado < 300:

        flash("Usuario actualizado correctamente.", "success")

        return redirect(
            url_for(
                "admin.admin_usuarios",
                buscar=buscar
            )
        )

    flash(mensaje_error(respuesta), "error")

    return redirect(
        url_for(
            "admin.admin_usuarios",
            editar=id,
            buscar=buscar
        )
    )
