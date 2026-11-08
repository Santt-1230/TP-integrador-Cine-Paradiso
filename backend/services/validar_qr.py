from repositories.validar_qr import (
    obtener_qr_entrada,
    obtener_qr_producto,
    validar_qr_entrada,
    validar_qr_producto
)


CATEGORIAS_PRODUCTOS = {
    "bebida",
    "comida",
    "estacionamiento",
    "vip"
}



def _error(codigo: str, mensaje: str, detalles: dict = None) -> dict:

    respuesta = {
        "valido": False,
        "codigo": codigo,
        "mensaje": mensaje
    }

    if detalles is not None:
        respuesta["detalles"] = detalles

    return respuesta

def _obtener_qr(token: str, tipo: str) -> dict | None:

    if tipo == "entrada":
        return obtener_qr_entrada(token)

    if tipo == "producto":
        return obtener_qr_producto(token)

    return None


def _comprobar_estado_qr(qr: dict) -> dict | None:

    estado = qr["estado_qr"]

    if estado == "utilizado":
        return _error(
            "QR_UTILIZADO",
            "Este QR ya fue utilizado.",
            qr
        )

    if estado == "cancelado":
        return _error(
            "QR_CANCELADO",
            "Este QR fue cancelado.",
            qr
        )

    if estado == "expirado":
        return _error(
            "QR_EXPIRADO",
            "Este QR está expirado.",
            qr
        )

    if estado != "valido":
        return _error(
            "QR_NO_VALIDO",
            "El QR no se encuentra disponible.",
            qr
        )

    return None

def _comprobar_entrada(qr: dict) -> dict | None:

    if qr["estado_compra"] != "confirmada":
        return _error(
            "COMPRA_NO_CONFIRMADA",
            "La compra no está confirmada.",
            qr
        )

    if qr["estado_entrada"] != "confirmada":
        return _error(
            "ENTRADA_NO_CONFIRMADA",
            "La entrada no está confirmada.",
            qr
        )

    if qr["estado_funcion"] != "programada":
        return _error(
            "FUNCION_NO_DISPONIBLE",
            "La función no está disponible.",
            qr
        )

    return None


def _comprobar_producto(qr: dict, categoria: str) -> dict | None:

    if categoria not in CATEGORIAS_PRODUCTOS:
        return _error(
            "CATEGORIA_INVALIDA",
            "La categoría seleccionada no es válida."
        )

    if qr["estado_compra"] != "confirmada":
        return _error(
            "COMPRA_NO_CONFIRMADA",
            "La compra no está confirmada.",
            qr
        )

    if qr["categoria"] != categoria:
        return _error(
            "CATEGORIA_INCORRECTA",
            "El QR no corresponde a la categoría seleccionada.",
            qr
        )

    return None

def _procesar_validacion(
    token: str,
    id_validador: int,
    tipo: str,
    categoria: str = None
) -> dict:


    qr = _obtener_qr(token, tipo)

    if qr is None:
        return _error(
            "QR_NO_EXISTE",
            "El QR no existe o no corresponde al tipo seleccionado."
        )


    error = _comprobar_estado_qr(qr)

    if error is not None:
        return error


    if tipo == "entrada":

        error = _comprobar_entrada(qr)

        if error is not None:
            return error

        resultado = validar_qr_entrada(
            token,
            id_validador
        )

    else:

        error = _comprobar_producto(qr, categoria)

        if error is not None:
            return error

        resultado = validar_qr_producto(
            token,
            id_validador,
            categoria
        )


    if resultado["filas"] <= 0:

        return _error(
            "QR_NO_VALIDADO",
            "No se pudo validar el QR. Es posible que haya sido utilizado por otro administrador."
        )


    qr_actualizado = _obtener_qr(token, tipo)

    if qr_actualizado is None:
        return _error(
            "ERROR_VALIDACION",
            "No se pudieron recuperar los datos del QR."
        )


    respuesta = {
        "valido": True,
        "mensaje": "QR validado correctamente."
    }

    if tipo == "entrada":

        respuesta["mensaje"] = "Entrada validada correctamente. Puede ingresar."
        respuesta["entrada"] = qr_actualizado

    else:

        respuesta["mensaje"] = "Producto validado correctamente. Puede realizar el retiro."
        respuesta["detalles"] = qr_actualizado

    return respuesta

def procesar_validacion_entrada(
    token: str,
    id_validador: int
) -> dict:

    return _procesar_validacion(
        token,
        id_validador,
        "entrada"
    )

def procesar_validacion_producto(
    token: str,
    id_validador: int,
    categoria: str
) -> dict:

    return _procesar_validacion(
        token,
        id_validador,
        "producto",
        categoria
    )