from decimal import Decimal, InvalidOperation

from flask import Blueprint, Response, abort, flash, jsonify, redirect, render_template, request, session, url_for
import requests

import api


compras_bp = Blueprint("compras_bp", __name__)

def leer_ids_promociones(fuente):
    valores = fuente.getlist("id_promociones")
    if not valores:
        promocion_anterior = fuente.get("id_promocion")
        valores = [promocion_anterior] if promocion_anterior else []
    try:
        ids = [int(valor) for valor in valores if valor]
    except ValueError:
        abort(400)
    if any(id_promocion < 1 for id_promocion in ids) or len(set(ids)) != len(ids):
        abort(400)
    return ids

def validar_seleccion_checkout(id_funcion, ids_butacas):
    return (
        id_funcion > 0
        and 1 <= len(ids_butacas) <= 6
        and all(id_butaca > 0 for id_butaca in ids_butacas)
        and len(set(ids_butacas)) == len(ids_butacas)
    )

@compras_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        try:
            id_funcion = int(request.form.get("id_funcion", ""))
            ids_butacas = [int(id_butaca) for id_butaca in request.form.getlist("butacas")]
            ids_promociones = leer_ids_promociones(request.form)
        except ValueError:
            abort(400)

        if not validar_seleccion_checkout(id_funcion, ids_butacas):
            flash("Elegí entre una y seis butacas distintas.", "warning")
            return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

        return redirect(url_for(
            "compras_bp.checkout_servicios",
            id_funcion=id_funcion,
            butacas=ids_butacas,
            id_promociones=ids_promociones,
        ))

    try:
        id_funcion = int(request.args.get("id_funcion", ""))
        butacas_recibidas = request.args.getlist("butacas")
        vienen_separadas_por_coma = len(butacas_recibidas) == 1 and "," in butacas_recibidas[0]
        if vienen_separadas_por_coma:
            butacas_recibidas = butacas_recibidas[0].split(",")
        ids_butacas = [int(id_butaca) for id_butaca in butacas_recibidas if id_butaca]
        ids_promociones = leer_ids_promociones(request.args)
    except ValueError:
        abort(400)

    if len(ids_butacas) > 6:
        flash("Podés seleccionar hasta seis butacas. Volvé a elegirlas.", "warning")
        return redirect(url_for("funciones_front.pagina_butacas", id_funcion=id_funcion))

    return render_checkout(id_funcion, ids_butacas, ids_promociones_seleccionadas=ids_promociones)



@compras_bp.route("/checkout/servicios", methods=["GET", "POST"])
def checkout_servicios():
    fuente = request.form if request.method == "POST" else request.args
    try:
        id_funcion = int(fuente.get("id_funcion", ""))
        valores_butacas = fuente.getlist("butacas")
        if len(valores_butacas) == 1 and "," in valores_butacas[0]:
            valores_butacas = valores_butacas[0].split(",")
        ids_butacas = [int(valor) for valor in valores_butacas if valor]
        ids_promociones = leer_ids_promociones(fuente)
    except ValueError:
        abort(400)

    if not validar_seleccion_checkout(id_funcion, ids_butacas):
        abort(400)

    if request.method == "POST":
        try:
            productos_elegidos = []
            for id_producto in request.form.getlist("productos"):
                cantidad_texto = request.form.get(f"cantidad_{id_producto}", "1")
                productos_elegidos.append({
                    "id_producto": int(id_producto),
                    "cantidad": int(cantidad_texto),
                })
        except ValueError:
            abort(400)

        estado_respuesta, cuerpo_respuesta = api.pedir(
            "POST",
            "/api/compras",
            datos={
                "id_funcion": id_funcion,
                "id_butacas": ids_butacas,
                "productos": productos_elegidos,
                "id_promociones": ids_promociones,
            },
        )
        if estado_respuesta == 201:
            return redirect(url_for("perfil.perfil_seccion", seccion="mis-compras"))

        cantidades = {producto["id_producto"]: producto["cantidad"] for producto in productos_elegidos}
        return render_servicios_checkout(
            id_funcion, ids_butacas, ids_promociones,
            productos_seleccionados=cantidades,
            error=api.mensaje_error(cuerpo_respuesta),
        )

    return render_servicios_checkout(id_funcion, ids_butacas, ids_promociones)


def render_checkout(id_funcion, ids_butacas, ids_promociones_seleccionadas=None, error=None):
    id_funcion_invalido = id_funcion < 1
    cantidad_butacas_invalida = not 1 <= len(ids_butacas) <= 6
    hay_id_butaca_invalido = any(id_butaca < 1 for id_butaca in ids_butacas)
    hay_butacas_repetidas = len(set(ids_butacas)) != len(ids_butacas)
    if id_funcion_invalido or cantidad_butacas_invalida or hay_id_butaca_invalido:
        abort(400)
    if hay_butacas_repetidas:
        abort(400)

    estado_funcion, datos_funcion = api.pedir("GET", f"/api/funciones/{id_funcion}")
    estado_butacas, datos_butacas = api.pedir("GET", f"/api/funciones/{id_funcion}/butacas")
    estado_promociones, datos_promociones = api.pedir("GET", "/api/promociones")

    funcion_cargada = estado_funcion == 200
    butacas_cargadas = estado_butacas == 200

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

    promociones = datos_promociones if estado_promociones == 200 and isinstance(datos_promociones, list) else []
    promociones = [promo for promo in promociones if promo.get("estado") == "Activa"]

    try:
        precio_entrada = Decimal(str(funcion["precio_entrada"])) if funcion else Decimal("0")
    except (InvalidOperation, KeyError):
        precio_entrada = Decimal("0")

    if funcion:
        funcion["precio_entrada"] = precio_entrada

    total = precio_entrada * len(ids_butacas)

    return render_template(
        "checkout.html",
        funcion=funcion,
        id_funcion=id_funcion,
        butacas=butacas,
        ids_butacas=ids_butacas,
        promociones=promociones,
        ids_promociones_seleccionadas=ids_promociones_seleccionadas or [],
        total=total,
        error=error,
    )


def render_servicios_checkout(id_funcion, ids_butacas, ids_promociones, productos_seleccionados=None, error=None):
    estado_funcion, datos_funcion = api.pedir("GET", f"/api/funciones/{id_funcion}")
    estado_butacas, datos_butacas = api.pedir("GET", f"/api/funciones/{id_funcion}/butacas")
    estado_servicios, datos_servicios = api.pedir("GET", "/api/servicios")
    estado_promociones, datos_promociones = api.pedir("GET", "/api/promociones")

    funcion = datos_funcion.get("funcion") if estado_funcion == 200 else None
    mapa = datos_butacas.get("butacas", []) if estado_butacas == 200 else []
    butacas_por_id = {butaca["id_butaca"]: butaca for butaca in mapa}
    butacas = [butacas_por_id[id_butaca] for id_butaca in ids_butacas if id_butaca in butacas_por_id]
    if not funcion:
        error = error or api.mensaje_error(datos_funcion)
    elif len(butacas) != len(ids_butacas):
        error = error or "Alguna de las butacas seleccionadas ya no existe para esta función."

    servicios = []
    servicios_error = None
    if estado_servicios == 200:
        if isinstance(datos_servicios, list):
            servicios = datos_servicios
        elif isinstance(datos_servicios, dict):
            servicios = datos_servicios.get("servicios", [])
    else:
        servicios_error = api.mensaje_error(datos_servicios)

    promociones = datos_promociones if estado_promociones == 200 and isinstance(datos_promociones, list) else []
    promociones = [promo for promo in promociones if promo.get("estado") == "Activa"]
    promociones_seleccionadas = [
        promo for promo in promociones
        if str(promo.get("id_promocion")) in {str(id_promocion) for id_promocion in ids_promociones}
    ]

    try:
        precio_entrada = Decimal(str(funcion["precio_entrada"])) if funcion else Decimal("0")
    except (InvalidOperation, KeyError, TypeError):
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

    total_entradas = precio_entrada * len(ids_butacas)
    return render_template(
        "checkout_servicios.html",
        funcion=funcion,
        id_funcion=id_funcion,
        ids_butacas=ids_butacas,
        butacas=butacas,
        productos=servicios,
        servicios_error=servicios_error,
        promociones=promociones,
        promociones_seleccionadas=promociones_seleccionadas,
        ids_promociones=ids_promociones,
        total=total_entradas,
        error=error,
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


@compras_bp.get("/mi-cuenta/compras/<int:id_compra>/qr")
def descargar_qrs(id_compra):
    if not session.get("id_usuario") or not session.get("cookie_backend"):
        return redirect(url_for("usuarios.login"))

    try:
        respuesta = requests.get(f"{api.BACKEND_URL}/api/compras/{id_compra}/qr",cookies=api.cookies_backend(),timeout=10,)
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
        headers={"Content-Disposition": f'attachment; filename="entradas-compra-{id_compra}.pdf"'},
    
    )