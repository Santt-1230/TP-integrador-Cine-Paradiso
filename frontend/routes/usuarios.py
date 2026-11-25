from datetime import date, timedelta

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session
)

import api


usuarios_bp = Blueprint("usuarios", __name__)


CLAVES_USUARIO = (
    "id_usuario",
    "nombre",
    "apellido",
    "rol",
    "cookie_backend"
)

def guardar_sesion(usuario):

    session["id_usuario"] = usuario["id_usuario"]
    session["nombre"] = usuario["nombre"]
    session["apellido"] = usuario["apellido"]
    session["rol"] = usuario["rol"]


def limpiar_sesion():

    for clave in CLAVES_USUARIO:
        session.pop(clave, None)


def manejar_sesion_expirada(estado):

    if estado == 401:
        limpiar_sesion()
        return redirect(url_for("usuarios.login"))

    return None


def render_cuenta(usuario=None, error=None, mensaje=None):

    if usuario is None:

        estado, usuario = api.pedir(
            "GET",
            "/api/usuarios/me"
        )

        redireccion = manejar_sesion_expirada(estado)

        if redireccion:
            return redireccion

        if estado != 200:

            return render_template(
                "mi_cuenta.html",
                usuario=None,
                error=api.mensaje_error(usuario)
            )

    return render_template(
        "mi_cuenta.html",
        usuario=usuario,
        error=error,
        mensaje=mensaje
    )


def actualizar_perfil(datos, mensaje_ok):

    estado, usuario = api.pedir(
        "PATCH",
        "/api/usuarios/me",
        datos=datos
    )

    redireccion = manejar_sesion_expirada(estado)

    if redireccion:
        return redireccion

    if estado < 200 or estado >= 300:

        return render_cuenta(
            error=api.mensaje_error(usuario)
        )

    guardar_sesion(usuario)

    return render_cuenta(
        usuario=usuario,
        mensaje=mensaje_ok
    )


@usuarios_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    datos = {
        "email": request.form.get("email", ""),
        "contrasena": request.form.get("contrasena", "")
    }

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/login",
        datos=datos
    )

    if estado < 200 or estado >= 300:

        mensaje = api.mensaje_error(respuesta)

        if estado == 403:

            return render_template(
                "confirmar_email.html",
                email=datos["email"],
                error=mensaje
            )

        return render_template(
            "login.html",
            error=mensaje
        )

    usuario = respuesta["usuario"]

    guardar_sesion(usuario)

    if usuario["rol"] == "administrador":

        return redirect(
            url_for("admin.admin")
        )

    return redirect(
        url_for("peliculas_front.inicio")
    )

@usuarios_bp.route("/registro", methods=["GET", "POST"])
def registro():

    ayer = (
        date.today() - timedelta(days=1)
    ).isoformat()

    if request.method == "GET":

        return render_template(
            "registro.html",
            fecha_maxima=ayer
        )

    campos = (
        "nombre",
        "apellido",
        "email",
        "fecha_nacimiento",
        "contrasena",
        "repetir_contrasena"
    )

    datos = {
        campo: request.form.get(campo, "")
        for campo in campos
    }

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/registro",
        datos=datos
    )

    if estado < 200 or estado >= 300:

        mensaje = api.mensaje_error(respuesta)

        if estado == 502:

            return render_template(
                "confirmar_email.html",
                email=datos["email"],
                error=mensaje
            )

        return render_template(
            "registro.html",
            error=mensaje,
            fecha_maxima=ayer
        )

    return render_template(
        "confirmar_email.html",
        email=datos["email"]
    )


@usuarios_bp.route("/verificar-email")
def verificar_email():

    token = request.args.get("token", "")

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/verificar-email",
        datos={"token": token}
    )

    if estado < 200 or estado >= 300:

        return render_template(
            "verificar_email.html",
            error=api.mensaje_error(respuesta)
        )

    return render_template(
        "verificar_email.html",
        ok=True
    )

@usuarios_bp.route("/reenviar-verificacion", methods=["POST"])
def reenviar_verificacion():

    email = request.form.get("email", "")

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/reenviar-verificacion",
        datos={"email": email}
    )

    if estado < 200 or estado >= 300:

        return render_template(
            "confirmar_email.html",
            email=email,
            error=api.mensaje_error(respuesta)
        )

    return render_template(
        "confirmar_email.html",
        email=email,
        mensaje="Si el email está pendiente de confirmación, te enviamos un nuevo mail."
    )

@usuarios_bp.route("/olvide-contrasena", methods=["GET", "POST"])
def olvide_contrasena():

    if request.method == "GET":
        return render_template("olvide_contrasena.html")

    email = request.form.get("email", "")

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/olvide-contrasena",
        datos={"email": email}
    )

    if estado < 200 or estado >= 300:

        return render_template(
            "olvide_contrasena.html",
            error=api.mensaje_error(respuesta)
        )

    return render_template(
        "olvide_contrasena.html",
        mensaje="Si el email tiene una cuenta, te enviamos un mail para cambiar la contraseña."
    )

@usuarios_bp.route("/restablecer-contrasena", methods=["GET", "POST"])
def restablecer_contrasena():

    if request.method == "GET":

        return render_template(
            "restablecer_contrasena.html",
            token=request.args.get("token", "")
        )

    campos = (
        "token",
        "contrasena_nueva",
        "repetir_contrasena"
    )

    datos = {
        campo: request.form.get(campo, "")
        for campo in campos
    }

    estado, respuesta = api.pedir(
        "POST",
        "/api/auth/restablecer-contrasena",
        datos=datos
    )

    if estado < 200 or estado >= 300:

        return render_template(
            "restablecer_contrasena.html",
            token=datos["token"],
            error=api.mensaje_error(respuesta)
        )

    return render_template(
        "restablecer_contrasena.html",
        ok=True
    )

@usuarios_bp.route("/mi-cuenta", methods=["GET", "POST"])
def mi_cuenta():

    if not session.get("id_usuario"):

        return redirect(
            url_for("usuarios.login")
        )

    if request.method == "GET":
        return render_cuenta()

    datos = {
        "nombre": request.form.get("nombre", ""),
        "apellido": request.form.get("apellido", "")
    }

    return actualizar_perfil(
        datos,
        "Datos actualizados correctamente"
    )


@usuarios_bp.route("/mi-cuenta/correo", methods=["POST"])
def cambiar_correo():

    if not session.get("id_usuario"):

        return redirect(
            url_for("usuarios.login")
        )

    datos = {
        "email": request.form.get("email", "")
    }

    return actualizar_perfil(
        datos,
        "Correo actualizado correctamente"
    )


@usuarios_bp.route("/mi-cuenta/password", methods=["POST"])
def cambiar_contrasena():

    if not session.get("id_usuario"):

        return redirect(
            url_for("usuarios.login")
        )

    campos = (
        "contrasena_actual",
        "contrasena_nueva",
        "repetir_contrasena"
    )

    datos = {
        campo: request.form.get(campo, "")
        for campo in campos
    }

    estado, respuesta = api.pedir(
        "PATCH",
        "/api/usuarios/me/password",
        datos=datos
    )

    redireccion = manejar_sesion_expirada(estado)

    if redireccion:
        return redireccion

    if estado < 200 or estado >= 300:

        return render_cuenta(
            error=api.mensaje_error(respuesta)
        )

    return render_cuenta(
        mensaje="Contraseña actualizada correctamente"
    )


@usuarios_bp.route("/logout", methods=["POST"])
def logout():

    api.pedir(
        "POST",
        "/api/auth/logout"
    )

    limpiar_sesion()

    return redirect(
        url_for("peliculas_front.inicio")
    )
