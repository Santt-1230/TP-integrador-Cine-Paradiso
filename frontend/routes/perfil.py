from flask import Blueprint, flash, redirect, render_template, session, url_for
from api import pedir, ApiError

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/mi-perfil')
def perfil():
    if "cookie_backend" not in session:
        return redirect(url_for("usuarios.login"))

    datos, historial = {}, {}
    try:
        datos = pedir("GET", "/api/usuarios/me")
        historial = pedir("GET", "/api/usuarios/me/historial")
    except ApiError as e:
        if e.estado == 401:
            return redirect(url_for("usuarios.login"))
        flash(e.mensaje)
    
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
    return render_template("perfil.html", perfil=datos, historial=historial)

  #  print("CLAVES HISTORIAL:", list(historial.keys()) if isinstance(historial, dict) else type(historial), flush=True)
  #  return render_template("perfil.html", perfil=datos, historial=historial)