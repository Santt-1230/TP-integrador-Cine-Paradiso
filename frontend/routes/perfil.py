import io
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for
from api import BACKEND_URL, cookies_backend, limpiar_sesion_front, mensaje_error, pedir, verificar_estado


perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('/mi-perfil', defaults={'seccion': 'mi-cuenta'})
@perfil_bp.route('/mi-perfil/<seccion>')
def perfil_seccion(seccion):
    secciones_validas = (
        "mi-cuenta",
        "peliculas-vistas",
        "mis-compras",
        "resenas",
        "cupones-y-puntos",
        "merch",
        "tu-opinion",
    )
    if seccion not in secciones_validas:
        return render_template("error.html"), 404

    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    datos = {}
    historial = {"compras": [], "peliculas_vistas": []}

    # 1. Datos personales del usuario
    estado, res_datos = pedir("GET", "/api/usuarios/me")
    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado == 200:
        datos = res_datos or {}
    else:
        flash(mensaje_error(res_datos), "error")

    # 2. Historial real desde el backend
    if seccion in ("mis-compras", "peliculas-vistas"):
        estado_h, res_hist = pedir("GET", "/api/usuarios/me/historial")
        redir_h = verificar_estado(estado_h)
        if redir_h:
            return redir_h

        if estado_h == 200:
            if isinstance(res_hist, list):
                historial = {"compras": res_hist, "peliculas_vistas": []}
            elif isinstance(res_hist, dict):
                historial = res_hist
        else:
            flash(mensaje_error(res_hist), "error")

    # 3. Enriquecer cada compra con los datos de su función y entradas
    if seccion == 'mis-compras':
        zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")
        ahora = datetime.now(zona_ar)
        compras_activas = []
        cache_funciones = {}

        for compra in (historial.get("compras") or []):
            if compra.get("estado") == "cancelada":
                continue

            # Buscar datos de la función (película, póster, sala, horario)
            id_funcion = compra.get("id_funcion")
            if id_funcion and id_funcion not in cache_funciones:
                est_f, res_f = pedir("GET", f"/api/funciones/{id_funcion}")
                if est_f == 200 and isinstance(res_f, dict):
                    print("DATOS FUNCION:", res_f, flush=True)
                    cache_funciones[id_funcion] = res_f.get("funcion") or res_f
                else:
                    cache_funciones[id_funcion] = {}

            funcion = cache_funciones.get(id_funcion, {})
            pelicula = funcion.get("pelicula") if isinstance(funcion.get("pelicula"), dict) else {}
            sala = funcion.get("sala") if isinstance(funcion.get("sala"), dict) else {}
            local = funcion.get("local") if isinstance(funcion.get("local"), dict) else {}

            # Título, póster y género
            compra["titulo_pelicula"] = (
                pelicula.get("titulo")
                or funcion.get("titulo_pelicula")
                or funcion.get("titulo")
                or (funcion.get("pelicula") if isinstance(funcion.get("pelicula"), str) else None)
                or "Película"
            )
            compra["poster_url"] = (
                pelicula.get("poster_url")
                or pelicula.get("imagen_url")
                or funcion.get("poster_url")
                or funcion.get("imagen_url")
                or ""
            )
            compra["genero"] = (
                pelicula.get("genero")
                or funcion.get("genero")
                or "CINE"
            )

            # Local, sala y butacas armadas desde 'entradas'
            compra["local"] = local.get("nombre") or funcion.get("local_nombre") or funcion.get("local") or ""
            compra["numero_sala"] = sala.get("numero_sala") or sala.get("numero") or funcion.get("numero_sala") or ""

            entradas = compra.get("entradas") or []
            butacas_ordenadas = sorted(entradas, key=lambda e: (str(e.get("fila", "")), int(e.get("numero", 0))))
            compra["butacas"] = ", ".join(f"{e.get('fila', '')}{e.get('numero', '')}" for e in butacas_ordenadas)

            # Normalizar imágenes de combos/servicios
            for srv in (compra.get("servicios") or []):
                if not srv.get("imagen_url"):
                    srv["imagen_url"] = srv.get("imagen") or srv.get("foto_url") or ""

            # Fecha de inicio de función (para mostrar arriba y habilitar cancelación)
            valor_fecha = funcion.get("fecha_hora_inicio") or compra.get("fecha_hora")
            if valor_fecha:
                try:
                    inicio_funcion = datetime.fromisoformat(str(valor_fecha).replace("Z", "+00:00"))
                    if inicio_funcion.tzinfo is None:
                        inicio_funcion = inicio_funcion.replace(tzinfo=zona_ar)
                    else:
                        inicio_funcion = inicio_funcion.astimezone(zona_ar)

                    # Solo habilita cancelar si tenemos el horario real de la función
                    if funcion.get("fecha_hora_inicio"):
                        compra["puede_cancelar"] = ahora < (inicio_funcion - timedelta(hours=1))
                    else:
                        compra["puede_cancelar"] = False

                    compra["fecha_formateada"] = inicio_funcion.strftime("%d/%m/%Y - %H:%M HS")
                    compra["fecha_hora_inicio"] = inicio_funcion.isoformat()
                except ValueError:
                    compra["puede_cancelar"] = False
                    compra["fecha_formateada"] = str(valor_fecha)
            else:
                compra["puede_cancelar"] = False
                compra["fecha_formateada"] = ""

            compras_activas.append(compra)

        historial["compras"] = compras_activas

    return render_template("perfil.html", perfil=datos, historial=historial, seccion=seccion)


@perfil_bp.route('/mi-perfil/mi-cuenta', methods=['POST'])
def cambiar_clave():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    actual = request.form.get("clave_actual", "")
    nueva = request.form.get("nueva_clave", "")
    confirmar = request.form.get("confirmar_clave", "")

    if nueva != confirmar:
        flash("Las contraseñas nuevas no coinciden.", "clave_error")
        return redirect(url_for("perfil.perfil_seccion", seccion="mi-cuenta"))

    estado, datos = pedir(
        "PATCH",
        "/api/usuarios/me/password",
        {"contrasena_actual": actual, "contrasena_nueva": nueva}
    )

    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado == 200:
        flash("¡Contraseña actualizada con éxito!", "clave_exito")
    else:
        flash(mensaje_error(datos), "clave_error")

    return redirect(url_for("perfil.perfil_seccion", seccion="mi-cuenta"))


@perfil_bp.route('/mi-perfil/actualizar-datos', methods=['POST'])
def actualizar_datos():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

    datos_actualizados = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "fecha_nacimiento": fecha_nacimiento,
    }

    estado, datos = pedir("PATCH", "/api/usuarios/me", datos_actualizados)

    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado == 200:
        session["nombre"] = nombre
        flash("Datos personales actualizados correctamente.", "exito")
    else:
        flash(mensaje_error(datos), "error")

    return redirect(url_for("perfil.perfil_seccion", seccion="mi-cuenta"))


@perfil_bp.route('/mi-perfil/baja', methods=['POST'])
def baja_cuenta():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    estado, datos = pedir("PATCH", "/api/usuarios/me/arrepentimiento")

    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado == 200:
        limpiar_sesion_front()
        flash("Tu cuenta fue dada de baja.", "exito")
        return redirect("/")

    flash(mensaje_error(datos), "error")
    return redirect(url_for("perfil.perfil_seccion", seccion="mi-cuenta"))


@perfil_bp.route('/mi-perfil/mis-compras', methods=['POST'])
def cancelar_compra():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    id_compra = request.form.get('id_compra')

    if id_compra:
        payload = {"estado": "cancelada"}
        estado, datos = pedir("PATCH", f"/api/compras/{id_compra}", payload)

        redir = verificar_estado(estado)
        if redir:
            return redir

        if estado == 200 and isinstance(datos, dict) and datos.get("exito"):
            flash('Compra cancelada exitosamente.', 'success')
        else:
            mensaje = datos.get("mensaje", "No se pudo cancelar la compra.") if isinstance(datos, dict) else "No se pudo cancelar la compra."
            flash(mensaje, 'error')

    return redirect(url_for('perfil.perfil_seccion', seccion='mis-compras'))


@perfil_bp.route('/mi-perfil/mis-compras/<int:id_compra>/pdf')
def descargar_pdf_compra(id_compra):
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    try:
        respuesta = requests.get(
            f"{BACKEND_URL}/api/compras/{id_compra}/pdf",
            cookies=cookies_backend(),
            timeout=15,
        )
    except requests.RequestException:
        flash("No se pudo conectar con el servidor.", "error")
        return redirect(url_for("perfil.perfil_seccion", seccion="mis-compras"))

    redir = verificar_estado(respuesta.status_code)
    if redir:
        return redir

    if respuesta.status_code != 200:
        flash("No se pudo descargar el comprobante.", "error")
        return redirect(url_for("perfil.perfil_seccion", seccion="mis-compras"))

    return send_file(
        io.BytesIO(respuesta.content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'factura_compra_{id_compra}.pdf',
    )