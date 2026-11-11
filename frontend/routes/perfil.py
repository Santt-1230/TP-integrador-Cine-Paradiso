import io
import requests
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from api import pedir, mensaje_error, verificar_estado, limpiar_sesion_front
from flask import send_file, session, flash, redirect, url_for
from api import BACKEND_URL, cookies_backend, verificar_estado

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
            historial = res_hist

    historial = {
        "peliculas_vistas": [
            {
                "id_pelicula": 1,
                "titulo": "El Padrino",
                "poster_url": "https://via.placeholder.com/150x225?text=El+Padrino",
                "duracion_min": 175,
                "clasificacion": "+18"
            },
            {
                "id_pelicula": 2,
                "titulo": "Interstellar",
                "poster_url": "https://via.placeholder.com/150x225?text=Interstellar",
                "duracion_min": 169,
                "clasificacion": "PG-13"
            }
        ],
        "compras": [
            {
                "id_compra": 101,
                "fecha_creacion": "27/10 - 20:30 HS",
                "titulo_pelicula": "PELICULA 1",
                "genero": "GÉNERO",
                "poster_url": "https://url-del-poster.com/imagen.jpg",
                "servicios": [
                    {
                        "nombre": "COMBO 1",
                        "imagen_url": "https://url-del-combo.com/combo.jpg"
                    }
                ]
            }
        ]
    }

    print("CLAVES HISTORIAL (MOCK):", list(historial.keys()), flush=True)
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
        estado, datos = pedir("POST", f"/api/compras/{id_compra}/cancelar")

        redir = verificar_estado(estado)
        if redir:
            return redir

        if estado == 200:
            flash('Compra cancelada correctamente.', 'success')
        else:
            flash(mensaje_error(datos), 'error')

    return redirect(url_for('perfil.perfil_seccion', seccion='mis-compras'))


@perfil_bp.route('/mi-perfil/mis-compras/<int:compra_id>/descargar-pdf')
def descargar_pdf_compra(compra_id):
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    try:
        # Petición directa al backend enviando la cookie de sesión
        respuesta = requests.get(
            f"{BACKEND_URL}/api/compras/{compra_id}/pdf",
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
        download_name=f'factura_compra_{compra_id}.pdf'
    )