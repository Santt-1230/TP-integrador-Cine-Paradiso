from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import api

servicios_bp = Blueprint("servicios", __name__)

TIPOS = ("Comida", "Bebida", "Estacionamiento", "VIP")

def redirigir_al_login():
    return redirect(url_for("usuarios.login"))


def redirigir_al_inicio():
    return redirect(url_for("peliculas_front.inicio"))


def redirigir_al_listado():
    return redirect(url_for("servicios.admin_servicios"))


def verificar_admin():
    if not session.get("id_usuario"):
        return redirigir_al_login()
    if session.get("rol") != "administrador":
        flash("No tenes permisos para acceder a esta seccion.", "error")
        return redirigir_al_inicio()
    return None


def verificar_estado(estado):
    if estado == 401:
        return redirigir_al_login()
    if estado == 403:
        return redirigir_al_inicio()
    return None


def datos_del_formulario():
    precio = request.form.get("precio", "").strip()
    try:
        precio = float(precio)
    except ValueError:
        pass
    descripcion = request.form.get("descripcion", "").strip()
    imagen_url = request.form.get("imagen_url", "").strip()
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "tipo": request.form.get("tipo", ""),
        "descripcion": descripcion or None,
        "precio": precio,
        "activo": "activo" in request.form,
        "imagen_url": imagen_url or None,
    }


def datos_de_promocion():
    descripcion = request.form.get("descripcion", "").strip()
    imagen_url = request.form.get("imagen_url", "").strip()
    tipo = request.form.get("tipo", "")
    cantidad_comprar = request.form.get("cantidad_comprar", "").strip()
    cantidad_pagar = request.form.get("cantidad_pagar", "").strip()
    porcentaje = request.form.get("porcentaje", "").strip()
    monto_descuento = request.form.get("monto_descuento", "").strip()

    try:
        cantidad_comprar = int(cantidad_comprar) if cantidad_comprar else None
    except ValueError:
        pass

    try:
        cantidad_pagar = int(cantidad_pagar) if cantidad_pagar else None
    except ValueError:
        pass

    try:
        porcentaje = float(porcentaje) if porcentaje else None
    except ValueError:
        pass

    try:
        monto_descuento = float(monto_descuento) if monto_descuento else None
    except ValueError:
        pass

    return {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": descripcion or None,
        "imagen_url": imagen_url or None,
        "vigente_desde": request.form.get("vigente_desde", ""),
        "vigente_hasta": request.form.get("vigente_hasta", ""),
        "activa": "activa" in request.form,
        "tipo": tipo,
        "cantidad_comprar": cantidad_comprar,
        "cantidad_pagar": cantidad_pagar,
        "porcentaje": porcentaje,
        "monto_descuento": monto_descuento,
    }


@servicios_bp.route("/servicios")
def servicios():
    estado_productos, productos = api.pedir("GET", "/api/servicios")
    estado_promociones, promociones = api.pedir("GET", "/api/promociones")
    error = None
    if estado_productos != 200:
        error = api.mensaje_error(productos)
        productos = []
    if estado_promociones != 200:
        error = error or api.mensaje_error(promociones)
        promociones = []
    return render_template("servicios.html", productos=productos, promociones=promociones, error=error)


@servicios_bp.route("/admin/servicios")
def admin_servicios():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    error = None
    estado, servicios = api.pedir("GET", "/api/servicios", params={"incluir_inactivos": "true"})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        error = api.mensaje_error(servicios)
        servicios = []
    estado, promociones = api.pedir("GET", "/api/promociones", params={"incluir_inactivas": "true"})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        error = error or api.mensaje_error(promociones)
        promociones = []
    return render_template("admin_servicios.html", servicios=servicios, promociones=promociones, error=error)


@servicios_bp.route("/admin/servicios/<int:id_producto>/dar-de-baja", methods=["POST"])
def admin_servicio_dar_de_baja(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("DELETE", f"/api/servicios/{id_producto}")
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/<int:id_producto>/activar", methods=["POST"])
def admin_servicio_activar(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("PATCH", f"/api/servicios/{id_producto}", {"activo": True})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/nuevo", methods=["GET", "POST"])
def admin_servicio_nuevo():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        return render_template("admin_servicio_form.html", servicio={}, tipos=TIPOS)
    datos = datos_del_formulario()
    estado, datos_respuesta = api.pedir("POST", "/api/servicios", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 201:
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()


@servicios_bp.route("/admin/servicios/<int:id_producto>/editar", methods=["GET", "POST"])
def admin_servicio_editar(id_producto):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        estado, datos_respuesta = api.pedir("GET", f"/api/servicios/{id_producto}")
        respuesta = verificar_estado(estado)
        if respuesta:
            return respuesta
        if estado != 200:
            flash(api.mensaje_error(datos_respuesta), "error")
            return redirigir_al_listado()
        return render_template("admin_servicio_form.html", servicio=datos_respuesta, tipos=TIPOS)
    datos = datos_del_formulario()
    estado, datos_respuesta = api.pedir("PATCH", f"/api/servicios/{id_producto}", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        datos["id_producto"] = id_producto
        return render_template("admin_servicio_form.html", servicio=datos, tipos=TIPOS,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()


@servicios_bp.route("/admin/promociones/nueva", methods=["GET", "POST"])
def admin_promocion_nueva():
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        return render_template("admin_promocion_form.html", promocion={})
    datos = datos_de_promocion()
    estado, datos_respuesta = api.pedir("POST", "/api/promociones", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 201:
        return render_template("admin_promocion_form.html", promocion=datos,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()


@servicios_bp.route("/admin/promociones/<int:id_promocion>/editar", methods=["GET", "POST"])
def admin_promocion_editar(id_promocion):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    if request.method == "GET":
        estado, datos_respuesta = api.pedir("GET", f"/api/promociones/{id_promocion}")
        respuesta = verificar_estado(estado)
        if respuesta:
            return respuesta
        if estado != 200:
            flash(api.mensaje_error(datos_respuesta), "error")
            return redirigir_al_listado()
        return render_template("admin_promocion_form.html", promocion=datos_respuesta)
    datos = datos_de_promocion()
    estado, datos_respuesta = api.pedir("PATCH", f"/api/promociones/{id_promocion}", datos)
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        datos["id_promocion"] = id_promocion
        return render_template("admin_promocion_form.html", promocion=datos,
                               error=api.mensaje_error(datos_respuesta))
    return redirigir_al_listado()


@servicios_bp.route("/admin/promociones/<int:id_promocion>/dar-de-baja", methods=["POST"])
def admin_promocion_dar_de_baja(id_promocion):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("DELETE", f"/api/promociones/{id_promocion}")
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()


@servicios_bp.route("/admin/promociones/<int:id_promocion>/activar", methods=["POST"])
def admin_promocion_activar(id_promocion):
    respuesta = verificar_admin()
    if respuesta:
        return respuesta
    estado, datos_respuesta = api.pedir("PATCH", f"/api/promociones/{id_promocion}", {"activa": True})
    respuesta = verificar_estado(estado)
    if respuesta:
        return respuesta
    if estado != 200:
        flash(api.mensaje_error(datos_respuesta), "error")
    return redirigir_al_listado()