from decimal import Decimal, InvalidOperation
import time

from flask import Blueprint, Response, abort, flash, jsonify, redirect, render_template, request, session, url_for
import requests

import api


compras_bp = Blueprint("compras_bp", __name__)

@compras_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        try:
            id_funcion = int(request.form.get("id_funcion", ""))
            ids_butacas = [int(id_butaca) for id_butaca in request.form.getlist("butacas")]
            productos_elegidos = []
            for id_producto in request.form.getlist("productos"):
                cantidad_texto = request.form.get(f"cantidad_{id_producto}", "1")
                productos_elegidos.append({
                    "id_producto": int(id_producto),
                    "cantidad": int(cantidad_texto),
                })
        except ValueError:
            abort(400)

        momento_de_expiracion = session.get("checkout_expira_en", 0)
        checkout_vencido = momento_de_expiracion <= time.time()
        if checkout_vencido:
            session.pop("checkout_expira_en", None)
            flash("Se venció el tiempo de checkout. Elegí las butacas nuevamente.", "warning")
            return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

        cantidad_de_butacas = len(ids_butacas)
        cantidad_permitida = 1 <= cantidad_de_butacas <= 6
        hay_butacas_repetidas = len(set(ids_butacas)) != cantidad_de_butacas
        if not cantidad_permitida or hay_butacas_repetidas:
            flash("Elegí entre una y seis butacas distintas.", "warning")
            return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

        estado_respuesta, cuerpo_respuesta = api.pedir_api(
            "POST",
            "/api/compras",
            cookies=api.cookies_backend(),
            json={
                "id_funcion": id_funcion,
                "id_butacas": ids_butacas,
                "productos": productos_elegidos,
            },
        )

        compra_creada = estado_respuesta == 201
        if compra_creada:
            session.pop("checkout_expira_en", None)
            flash("Compra registrada con exito", "mensaje-ok")
            return redirect(url_for("compras_bp.mis_compras"))

        cantidad_por_id_producto = {
            producto["id_producto"]: producto["cantidad"]
            for producto in productos_elegidos
        }
        return render_checkout(
            id_funcion,
            ids_butacas,
            error=api.mensaje_error(cuerpo_respuesta),
            productos_seleccionados=cantidad_por_id_producto,
        )

    try:
        id_funcion = int(request.args.get("id_funcion", ""))
        butacas_recibidas = request.args.getlist("butacas")
        vienen_separadas_por_coma = len(butacas_recibidas) == 1 and "," in butacas_recibidas[0]
        if vienen_separadas_por_coma:
            butacas_recibidas = butacas_recibidas[0].split(",")
        ids_butacas = [int(id_butaca) for id_butaca in butacas_recibidas if id_butaca]
    except ValueError:
        abort(400)

    if len(ids_butacas) > 6:
        flash("Podés seleccionar hasta seis butacas. Volvé a elegirlas.", "warning")
        return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

    momento_de_expiracion = session.get("checkout_expira_en")
    checkout_ya_iniciado = bool(momento_de_expiracion)
    checkout_vencido = checkout_ya_iniciado and momento_de_expiracion <= time.time()
    if checkout_vencido:
        session.pop("checkout_expira_en", None)
        flash("Se venció el tiempo de checkout. Elegí las butacas nuevamente.", "warning")
        return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

    if not checkout_ya_iniciado:
        session["checkout_expira_en"] = time.time() + 10 * 60

    return render_checkout(id_funcion, ids_butacas)

def render_checkout(id_funcion, ids_butacas, error=None, productos_seleccionados=None):
    id_funcion_invalido = id_funcion < 1
    cantidad_butacas_invalida = not 1 <= len(ids_butacas) <= 6
    hay_id_butaca_invalido = any(id_butaca < 1 for id_butaca in ids_butacas)
    hay_butacas_repetidas = len(set(ids_butacas)) != len(ids_butacas)
    if id_funcion_invalido or cantidad_butacas_invalida or hay_id_butaca_invalido:
        abort(400)
    if hay_butacas_repetidas:
        abort(400)

    estado_funcion, datos_funcion = api.pedir_api("GET", f"/api/funciones/{id_funcion}")
    estado_butacas, datos_butacas = api.pedir_api("GET", f"/api/funciones/{id_funcion}/butacas")
    estado_servicios, datos_servicios = api.pedir_api("GET", "/api/servicios")

    funcion_cargada = estado_funcion == 200
    butacas_cargadas = estado_butacas == 200
    servicios_cargados = estado_servicios == 200

    funcion = datos_funcion.get("funcion") if funcion_cargada else None
    mapa_butacas = datos_butacas.get("butacas", []) if butacas_cargadas else []

    butacas_por_id = {
        butaca["id_butaca"]: butaca
        for butaca in mapa_butacas
        if butaca.get("id_butaca") in ids_butacas
    }
    butacas = [
        butacas_por_id[id_butaca]
        for id_butaca in ids_butacas
        if id_butaca in butacas_por_id
    ]

    faltan_butacas = len(butacas) != len(ids_butacas)
    hay_butaca_no_disponible = any(butaca.get("estado") != "disponible" for butaca in butacas)

    if not funcion_cargada:
        error = error or api.mensaje_error(datos_funcion)
    elif not butacas_cargadas:
        error = error or api.mensaje_error(datos_butacas)
    elif faltan_butacas:
        error = error or "Alguna de las butacas seleccionadas ya no existe para esta función."
    elif hay_butaca_no_disponible:
        error = error or "Alguna butaca seleccionada dejó de estar disponible. Volvé al mapa y elegí otras."

    servicios = []
    servicios_error = None
    if servicios_cargados:
        if isinstance(datos_servicios, list):
            servicios = datos_servicios
        elif isinstance(datos_servicios, dict):
            servicios = datos_servicios.get("servicios", [])
    else:
        servicios_error = api.mensaje_error(datos_servicios)

    try:
        precio_entrada = Decimal(str(funcion["precio_entrada"])) if funcion else Decimal("0")
    except (InvalidOperation, KeyError):
        precio_entrada = Decimal("0")

    if funcion:
        funcion["precio_entrada"] = precio_entrada

    cantidades_elegidas = productos_seleccionados or {}
    for servicio in servicios:
        try:
            servicio["precio"] = Decimal(str(servicio["precio"]))
        except (InvalidOperation, KeyError, TypeError):
            servicio["precio"] = Decimal("0")
        servicio["cantidad_seleccionada"] = cantidades_elegidas.get(servicio.get("id_producto"), 0)

    total = precio_entrada * len(ids_butacas)

    expiracion_checkout = session.get("checkout_expira_en", time.time() + 10 * 60)

    return render_template(
        "checkout.html",
        funcion=funcion,
        id_funcion=id_funcion,
        butacas=butacas,
        ids_butacas=ids_butacas,
        productos=servicios,
        servicios_error=servicios_error,
        total=total,
        error=error,
        checkout_expira_en=expiracion_checkout,
        locales=[],
    )



@compras_bp.get("/mi-cuenta/compras/<int:id_compra>/factura")
def descargar_factura(id_compra):
    if not session.get("id_usuario") or not session.get("cookie_backend"):
        return redirect(url_for("usuarios.login"))

    try:
        respuesta = requests.get(f"{api.BACKEND_URL}/api/compras/{id_compra}/factura", cookies=api.cookies_backend(), timeout=10,)
    except requests.RequestException:
        abort(503, "No se pudo conectar con el servidor.")

    if respuesta.status_code == 401:
        for clave in ("cookie_backend", "id_usuario", "nombre", "apellido", "rol"):
            session.pop(clave, None)
        return redirect(url_for("usuarios.login"))
    if not respuesta.ok:
        try:
            return jsonify(respuesta.json()), respuesta.status_code
        except ValueError:
            abort(502, "El servidor devolvió una respuesta inválida.")

    return Response(
        respuesta.content,
        status=respuesta.status_code,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="factura-compra-{id_compra}.pdf"'},
    )