from repositories.validar_qr import (
    validar_qr,
    obtener_qr_entrada,
    obtener_qr_producto
)


def procesar_validacion_qr(token: str, id_validador: int, tipo: str) -> dict:

    obtener_qr_por_tipo = {
        "entrada": obtener_qr_entrada,
        "producto": obtener_qr_producto
    }

    obtener = obtener_qr_por_tipo.get(tipo)

    if obtener is None:
        raise ValueError("Tipo de QR inválido")

    resultado = validar_qr(token, id_validador, tipo)

    if resultado["filas"] == 1:

        qr = obtener(token)

        return {
            "valido": True,
            "mensaje": "QR validado correctamente",
            "entrada" if tipo == "entrada" else "detalles": qr
        }

    qr = obtener(token)

    if qr is None:
        return {
            "valido": False,
            "codigo": "QR_NO_EXISTE",
            "mensaje": "El QR no existe o no corresponde a este tipo"
        }

    if qr["estado"] == "utilizado":
        return {
            "valido": False,
            "codigo": "QR_UTILIZADO",
            "mensaje": "El QR ya fue utilizado",
            "detalles": qr
        }

    if qr["estado"] == "cancelado":
        return {
            "valido": False,
            "codigo": "QR_CANCELADO",
            "mensaje": "El QR fue cancelado",
            "detalles": qr
        }

    return {
        "valido": False,
        "codigo": "QR_NO_VALIDO",
        "mensaje": "No se pudo validar el QR",
        "detalles": qr
    }