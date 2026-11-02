from datetime import datetime, timedelta
from repositories.cancelaciones_repository import (
    ejecutar_cancelacion_bd,
    obtener_compra_para_cancelar,
)

MINUTOS_LIMITE_CANCELACION = 60

def procesar_cancelacion_cliente(id_compra: int, datos: dict | None = None) -> tuple[dict, int]:
    compra = obtener_compra_para_cancelar(id_compra)

    if not compra:
        return {"exito": False, "mensaje": "Compra no encontrada"}, 404

    if compra["estado"] == "cancelada":
        return {"exito": False, "mensaje": "La compra ya se encuentra cancelada"}, 400

    ahora = datetime.now()
    limite = compra["fecha_hora"] - timedelta(minutes=MINUTOS_LIMITE_CANCELACION)

    if ahora > limite:
        return {
            "exito": False,
            "mensaje": "Se ha superado el tiempo límite para cancelar la entrada (máximo 1 hora antes de la función)",
        }, 400

    monto_reembolso = float(compra["total"])
    ejecutar_cancelacion_bd(id_compra, monto_reembolso)

    return {
        "exito": True,
        "mensaje": "Compra cancelada correctamente",
        "monto_reembolsado": monto_reembolso,
    }, 200