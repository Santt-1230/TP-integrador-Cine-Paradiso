from utils import construir_error_api, validar_entero_positivo
import constants as const


def validar_datos(compra):
    if not isinstance(compra, dict):
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es invalido",
            description="Se esperaba un objeto JSON con id_funcion, id_butacas y productos",
        )
    funcion_id = compra.get("id_funcion")

    if funcion_id is None or str(funcion_id).strip() == "":
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es invalido",
            description="Al body recibido le falta id_funcion"
        )

    butacas = compra.get("id_butacas", compra.get("butacas"))

    if not isinstance(butacas, list) or len(butacas) == 0:
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es invalido",
            description="id_butacas debe ser una lista con al menos una butaca"
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

    productos = compra.get("productos", [])
    compra["butacas"] = butacas_ids
    if not isinstance(productos, list):
        return construir_error_api(
            code="PRODUCTOS_INVALIDOS",
            message="Productos inválidos",
            description="productos debe ser una lista",
        )
    productos_ids = set()
    for producto in productos:
        error = validar_datos_servicio(producto)
        if error:
            return error
        if producto["id_producto"] in productos_ids:
            return construir_error_api(
                code="PRODUCTO_DUPLICADO",
                message="Producto duplicado",
                description="Cada producto debe aparecer una sola vez en la compra",
            )
        productos_ids.add(producto["id_producto"])
    compra["productos"] = productos

    ids_promociones = compra.get("id_promociones")
    if ids_promociones is None:
        id_promocion_anterior = compra.get("id_promocion")
        ids_promociones = [] if id_promocion_anterior in (None, "") else [id_promocion_anterior]
    if not isinstance(ids_promociones, list):
        return construir_error_api(
            code="PROMOCIONES_INVALIDAS",
            message="Promociones inválidas",
            description="id_promociones debe ser una lista de identificadores",
        )

    promociones_ids = []
    for id_promocion in ids_promociones:
        try:
            promociones_ids.append(validar_entero_positivo(
                id_promocion, const.ENTERO_POSITIVO_MINIMO, "id_promocion"
            ))
        except ValueError:
            return construir_error_api(
                code="PROMOCION_INVALIDA",
                message="Promoción inválida",
                description="Cada identificador de promoción debe ser un entero positivo",
            )
    if len(set(promociones_ids)) != len(promociones_ids):
        return construir_error_api(
            code="PROMOCION_DUPLICADA",
            message="Promoción duplicada",
            description="No se puede aplicar la misma promoción más de una vez",
        )
    compra["id_promociones"] = promociones_ids

    return None

def validar_datos_servicio(datos):
    if not isinstance(datos, dict):
        return construir_error_api(
            code="BODY_INVALIDO",
            message="El body recibido es inválido",
            description="Se esperaba un objeto JSON con id_producto y cantidad",
        )

    id_producto = datos.get("id_producto")
    cantidad = datos.get("cantidad", 1)
    valores = ((id_producto, "id_producto"), (cantidad, "cantidad"))
    for valor, campo in valores:
        if isinstance(valor, bool) or not (
            isinstance(valor, int)
            or (isinstance(valor, str) and valor.strip().isdigit())
        ):
            return construir_error_api(
                code="DATOS_INVALIDOS",
                message="Parámetro inválido",
                description=f"'{campo}' debe ser un número entero positivo",
            )
        if int(valor) <= 0:
            return construir_error_api(
                code="DATOS_INVALIDOS",
                message="Parámetro inválido",
                description=f"'{campo}' debe ser mayor que cero",
            )

    datos["id_producto"] = int(id_producto)
    datos["cantidad"] = int(cantidad)
    return None