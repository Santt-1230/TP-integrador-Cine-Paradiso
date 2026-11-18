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
    if seccion not in ("mi-cuenta", "peliculas-vistas", "mis-compras", "resenas", "cupones-y-puntos", "merch", "tu-opinion"):
        return render_template("error.html"), 404
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    datos, historial = {}, {}

    estado, res_datos = pedir("GET", "/api/usuarios/me")
    redir = verificar_estado(estado)
    if redir:
        return redir

    if estado == 200:
        datos = res_datos
    else:
        flash(mensaje_error(res_datos), "error")

    if seccion in ("mis-compras", "peliculas-vistas"):
        estado_h, res_hist = pedir("GET", "/api/usuarios/me/historial")
        redir_h = verificar_estado(estado_h)
        if redir_h:
            return redir_h

        if estado_h == 200:
            historial = res_hist or {}
        else:
            flash(mensaje_error(res_hist), "error")

        # Procesamos las compras dentro de historial
    if seccion == 'mis-compras':
        ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        compras_activas = []

        for compra in historial.get("compras", []):
            if compra.get("estado") == "cancelada":
                continue

            valor_fecha = compra.get("fecha_hora_inicio")
            if valor_fecha:
                inicio_funcion = datetime.fromisoformat(str(valor_fecha))
                if inicio_funcion.tzinfo is None:
                    inicio_funcion = inicio_funcion.replace(tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
                compra["puede_cancelar"] = ahora < (inicio_funcion - timedelta(hours=1))
            else:
                compra["puede_cancelar"] = False

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

    estado, datos = pedir("PATCH", "/api/usuarios/me/password",
                          {"contrasena_actual": actual, "contrasena_nueva": nueva})

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
        "fecha_nacimiento": fecha_nacimiento
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

    comentario = request.form.get("comentario", "").strip()

    # Si la API en el backend acepta el comentario, se lo podés pasar como payload:
    # estado, datos = pedir("PATCH", "/api/usuarios/me/arrepentimiento", {"comentario": comentario})
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

        if estado == 200 and datos.get("exito"):
            flash('Compra cancelada exitosamente.', 'success')
        else:
            flash(datos.get("mensaje", "No se pudo cancelar la compra."), 'error')

    return redirect(url_for('perfil.perfil_seccion', seccion='mis-compras'))


@perfil_bp.route('/mi-perfil/mis-compras/<int:id_compra>/pdf')
def descargar_pdf_compra(id_compra):
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    try:
        # Petición directa al backend enviando la cookie de sesión
        respuesta = requests.get(
            f"{BACKEND_URL}/api/compras/{id_compra}/pdf",
            cookies=cookies_backend(),
            timeout=15
        )
    except requests.RequestException:
        flash("No se pudo conectar con el servidor.", "error")
        return redirect(url_for("perfil.perfil_seccion", seccion="mis-compras"))

    # Manejar expiración de sesión (401/403)
    redir = verificar_estado(respuesta.status_code)
    if redir:
        return redir

    if respuesta.status_code != 200:
        flash("No se pudo descargar el comprobante.", "error")
        return redirect(url_for("perfil.perfil_seccion", seccion="mis-compras"))

    # Forzar la descarga en el navegador
    return send_file(
        io.BytesIO(respuesta.content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'factura_compra_{id_compra}.pdf'
    )