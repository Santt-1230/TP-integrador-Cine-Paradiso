from datetime import date, datetime

from flask import Blueprint, render_template, url_for, flash, request, redirect

from api import (
    verificar_estado,
    pedir,
    mensaje_error,
    admin_front_requerido
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


TEXTO_ESTADO = {"vigente": "Vigente", "proxima": "Próxima"}


def _fecha_ar(texto):
    try:
        return date.fromisoformat(texto).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return "—"


def _contar_funciones(id_pelicula):
    estado, datos = pedir("GET", f"/api/peliculas/{id_pelicula}/funciones")
    if estado != 200:
        return "—"
    funciones = datos.get("funciones") if isinstance(datos, dict) else datos
    return len(funciones) if isinstance(funciones, list) else "—"


def _hora_funcion(texto):
    try:
        return datetime.fromisoformat(str(texto).replace(" ", "T")).replace(tzinfo=None)
    except ValueError:
        return None


def _proximas_funciones():
    # id de película -> lista de sus funciones que no terminaron, con el cine de cada una
    estado, datos = pedir("GET", "/api/funciones", params={"incluir_canceladas": "true"})
    funciones = datos.get("funciones", []) if estado == 200 and isinstance(datos, dict) else []
    ahora = datetime.now()
    lista = []
    for f in funciones:
        if f.get("estado") != "programada":
            continue
        inicio = _hora_funcion(f.get("fecha_hora_inicio"))
        fin = _hora_funcion(f.get("fecha_hora_fin"))
        if not inicio or not fin or fin <= ahora:
            continue
        cine = f.get("local")
        sufijo = " · " + cine if cine else ""
        if inicio <= ahora:
            candidata = (0, inicio, "En curso (hasta " + fin.strftime("%H:%M") + ")" + sufijo)
        else:
            candidata = (1, inicio, inicio.strftime("%d/%m %H:%M") + sufijo)
        lista.append((f.get("id_pelicula"), candidata))
    resultado = {}
    for id_pelicula, c in sorted(lista, key=lambda par: par[1][:2]):
        resultado.setdefault(id_pelicula, []).append(c[2])
    return resultado


def _cantidad_funciones():
    # funciones que todavía no terminaron (programadas o en curso), por película
    estado, datos = pedir("GET", "/api/funciones", params={"incluir_canceladas": "true"})
    funciones = datos.get("funciones", []) if estado == 200 and isinstance(datos, dict) else []
    ahora = datetime.now()
    cantidades = {}
    for f in funciones:
        fin = _hora_funcion(f.get("fecha_hora_fin"))
        if f.get("estado") == "programada" and fin and fin > ahora:
            id_pelicula = f.get("id_pelicula")
            cantidades[id_pelicula] = cantidades.get(id_pelicula, 0) + 1
    return cantidades


def _novedades_inicio():
    estado, respuesta = pedir("GET", "/api/admin/peliculas")
    if estado != 200 or not isinstance(respuesta, dict):
        print("Error al obtener las películas:", mensaje_error(respuesta))
        return []

    peliculas = [p for p in respuesta.get("peliculas", []) if p.get("estado_cartelera") in TEXTO_ESTADO]
    # primero las vigentes y después las próximas, por fecha de inicio
    peliculas.sort(key=lambda p: (p["estado_cartelera"] != "vigente", p.get("cartelera_desde") or ""))
    proximas = _proximas_funciones()
    cantidades = _cantidad_funciones()

    return [
        {
            "nombre": p.get("nombre"),
            "poster_url": p.get("poster_url"),
            "fecha_estreno": _fecha_ar(p.get("cartelera_desde")),
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
    # PELÍCULAS ACTIVAS
    # --------------------------------

    estado, respuesta = pedir(
        "GET",
        "/api/admin/peliculas/activa"
    )

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
    # OCUPACIÓN DE FUNCIONES
    # --------------------------------

    estado, ocupacion_por_funcion = pedir(
        "GET",
        "/api/estadisticas/ocupacion",
        params={"periodo": "30"}
    )

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

    novedades = _novedades_inicio()

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

        print("ID RECIBIDO:", editar_id)

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

        else:
            print("USUARIO OBTENIDO:", usuario_editar)

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
