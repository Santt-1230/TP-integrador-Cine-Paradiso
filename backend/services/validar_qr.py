from backend.repositories.validar_qr import validar_qr, obtener_qr


def procesar_validacion_qr(token: str, id_validador: int) -> dict:

    resultado = validar_qr(token, id_validador) #devuelve 1 si se modificó un registro, 0 si no se modificó ningún registro 

    if resultado["filas"] == 1:

        qr = obtener_qr(token)

        return {
            "valido": True,
            "mensaje": "QR aceptado",
            "datos": qr
        }

    qr = obtener_qr(token)

    if qr is None:
        return {
            "valido": False,
            "mensaje": "El QR no existe"
        }

    if qr["estado"] == "utilizado":
        return {
            "valido": False,
            "mensaje": "El QR ya fue utilizado",
            "fecha_uso": str(qr["fecha_uso"])
        }

    if qr["estado"] == "cancelado":
        return {
            "valido": False,
            "mensaje": "El QR fue cancelado"
        }

    return {
        "valido": False,
        "mensaje": "No se pudo validar el QR"
    }