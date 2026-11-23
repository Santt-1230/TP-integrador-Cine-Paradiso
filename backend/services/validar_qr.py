from repositories.validar_qr import (
    obtener_qr_entrada,
    obtener_qr_producto,
    validar_qr_entrada,
    validar_qr_producto
)
from validators.validar_qr import validar_categoria

def error_qr(codigo: str, mensaje: str, detalles: dict = None) -> dict:

    respuesta = {
        "valido": False,
        "codigo": codigo,
        "mensaje": mensaje
    }

    if detalles is not None:
        respuesta["detalles"] = detalles

    return respuesta

def obtener_qr(token: str, tipo: str) -> dict | None:

    if tipo == "entrada":
        return obtener_qr_entrada(token)

    if tipo == "producto":
        return obtener_qr_producto(token)

    return None


def comprobar_estado_qr(qr: dict) -> dict | None:

    estado = qr["estado_qr"]

    if estado == "utilizado":
        return error_qr(
            "QR_UTILIZADO",
            "Este QR ya fue utilizado.",
            qr
        )

    if estado == "cancelado":
        return error_qr(
            "QR_CANCELADO",
            "Este QR fue cancelado.",
            qr
        )

    if estado == "expirado":
        return error_qr(
            "QR_EXPIRADO",
            "Este QR está expirado.",
            qr
        )

    if estado != "valido":
        return error_qr(
            "QR_NO_VALIDO",
            "El QR no se encuentra disponible.",
            qr
        )

    return None

def comprobar_entrada(qr: dict) -> dict | None:

    if qr["estado_compra"] != "confirmada":
        return error_qr(
            "COMPRA_NO_CONFIRMADA",
            "La compra no está confirmada.",
            qr
        )

    if qr["estado_entrada"] != "confirmada":
        return error_qr(
            "ENTRADA_NO_CONFIRMADA",
            "La entrada no está confirmada.",
            qr
        )

    if qr["estado_funcion"] != "programada":
        return error_qr(
            "FUNCION_NO_DISPONIBLE",
            "La función no está disponible.",
            qr
        )

    return None


def comprobar_producto(qr: dict, categoria: str) -> dict | None:

    if not validar_categoria(categoria):
        return error_qr(
            "CATEGORIA_INVALIDA",
            "La categoría seleccionada no es válida."
        )

    if qr["estado_compra"] != "confirmada":
        return error_qr(
            "COMPRA_NO_CONFIRMADA",
            "La compra no está confirmada.",
            qr
        )

    if qr["categoria"] != categoria:
        return error_qr(
            "CATEGORIA_INCORRECTA",
            "El QR no corresponde a la categoría seleccionada.",
            qr
        )

    return None


def procesar_validacion(
    token: str,
    id_validador: int,
    tipo: str,
    categoria: str = None
) -> dict:


    qr = obtener_qr(token, tipo)

    if qr is None:
        return error_qr(
            "QR_NO_EXISTE",
            "El QR no existe o no corresponde al tipo seleccionado."
        )


    error = comprobar_estado_qr(qr)

    if error is not None:
        return error


    if tipo == "entrada":

        error = comprobar_entrada(qr)

        if error is not None:
            return error

        resultado = validar_qr_entrada(
            token,
            id_validador
        )

    else:

        error = comprobar_producto(qr, categoria)

        if error is not None:
            return error

        resultado = validar_qr_producto(
            token,
            id_validador,
            categoria
        )


    if resultado["filas"] <= 0:

        return error_qr(
            "QR_NO_VALIDADO",
            "No se pudo validar el QR. Es posible que haya sido utilizado por otro administrador."
        )


    qr_actualizado = obtener_qr(token, tipo)

    if qr_actualizado is None:
        return error_qr(
            "ERROR_VALIDACION",
            "No se pudieron recuperar los datos del QR."
        )


    respuesta = {
        "valido": True,
    }

    if tipo == "entrada":
        
        respuesta["mensaje"] = "Entrada validada correctamente. Puede ingresar."
        respuesta["entrada"] = qr_actualizado

    else:

        respuesta["mensaje"] = "Producto validado correctamente. Puede realizar el retiro."
        respuesta["detalles"] = qr_actualizado

    return respuesta

