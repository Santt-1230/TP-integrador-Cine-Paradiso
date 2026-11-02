from utils import construir_error_api, validar_entero_positivo
import constants as const


def validar_datos(compra):
    funcion_id = compra.get("id_funcion")

    if funcion_id is None or str(funcion_id).strip() == "":
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es invalido",
            description="Al body recibido le falta id_funcion"
        )
    butacas = compra.get("butacas")

    if not isinstance(butacas, list) or len(butacas) == 0:
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es invalido",
            description="Al body recibido le falta butaca/s"
        )
    if len(butacas) > 6:
            return construir_error_api(
                code="BUTACAS_INVALIDAS",
                message="Maxima butacas alcanzadas",
                description="Solo se puede reservar un maximo de 6 butacas"
            )
    

    try:
        butacas_ids = []
        validar_entero_positivo(funcion_id, const.ENTERO_POSITIVO_MINIMO, "id_funcion")
        for butaca in butacas:
            validar_entero_positivo(butaca,const.ENTERO_POSITIVO_MINIMO,"id_butaca")
            butacas_ids.append(int(butaca))
    except ValueError as error:
        return error.args[0]

    if len(set(butacas_ids)) != len(butacas_ids): 
        return construir_error_api(
            code="BUTACA_DUPLICADA",
            message="Butaca duplicada",
            description="No se puede elegir la misma butaca mas de una vez en una compra"
        )

    return None
