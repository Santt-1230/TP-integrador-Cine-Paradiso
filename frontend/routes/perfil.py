from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from api import pedir, ApiError

perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('/mi-perfil', defaults={'seccion': 'mi-cuenta'})
@perfil_bp.route('/mi-perfil/<seccion>')
def perfil_seccion(seccion):
    if seccion not in ("mi-cuenta", "peliculas-vistas", "mis-compras", "resenas", "cupones-y-puntos", "merch", "tu-opinion"):
        return render_template("error.html"), 404
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    datos, historial = {}, {}
    try:
        datos = pedir("GET", "/api/usuarios/me")
        if seccion in ("mis-compras", "peliculas-vistas"):
            historial = pedir("GET", "/api/usuarios/me/historial")
    except ApiError as e:
        if e.estado == 401:
            return redirect(url_for("usuarios.login"))
        flash(e.mensaje, "error")

 # datos de prueba para peliculas vistas y mis compras
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
            "poster_url": "https://url-del-poster.com/imagen.jpg", # Opcional
            "servicios": [
                {
                    "nombre": "COMBO 1",
                    "imagen_url": "https://url-del-combo.com/combo.jpg" # Opcional
                }
            ]
        }
    ]
    }

    print("CLAVES HISTORIAL (MOCK):", list(historial.keys()), flush=True)
    return render_template("perfil.html", perfil=datos, historial=historial, seccion=seccion)

  #  print("CLAVES HISTORIAL:", list(historial.keys()) if isinstance(historial, dict) else type(historial), flush=True)
  #  return render_template("perfil.html", perfil=datos, historial=historial)

@perfil_bp.route('/mi-perfil/mi-cuenta', methods=['POST'])
def cambiar_clave():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    actual = request.form.get("clave_actual", "")
    nueva = request.form.get("nueva_clave", "")
    confirmar = request.form.get("confirmar_clave", "")

    if nueva != confirmar:
        flash("Las contraseñas nuevas no coinciden.", "clave_error")
        return redirect(url_for("perfil.perfil"))

    try:
        pedir("PATCH", "/api/usuarios/me/password",
              {"contrasena_actual": actual, "contrasena_nueva": nueva})
        flash("¡Contraseña actualizada con éxito!", "clave_exito")
    except ApiError as e:
        if e.estado == 401:
            return redirect(url_for("usuarios.login"))
        flash(e.mensaje, "clave_error")
    return redirect(url_for("perfil.perfil"))
    
@perfil_bp.route('/mi-perfil/baja', methods=['POST'])
def baja_cuenta():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    try:
        pedir("PATCH", "/api/usuarios/me/arrepentimiento")
    except ApiError as e:
        session.clear()
        flash(e.mensaje, "error")
        return redirect(url_for("usuarios.login"))

    session.clear()
    flash("Tu cuenta fue dada de baja.", "exito")
    return redirect("/")