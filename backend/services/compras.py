from utils import construir_error_api
from repositories import compras as compras_repositories
from repositories import usuarios as usuarios_repositories
from validators import compras as compras_validators
from repositories import qr as qr_repositories
from repositories import peliculas as peliculas_repositories
from repositories import funciones as funciones_repositories
import constants as const
import secrets

def generar_token():
    return secrets.token_hex(32)

def generar_codigo_manual():
    return "".join(secrets.choice(const.ALFABETO_CODIGO) for _ in range(12))


def construir_compra(compra, pelicula, entradas, productos):
    return {
        "id": compra["id_compra"],
        "fecha": compra["fecha_creacion"],
        "fecha_confirmacion": compra.get("fecha_confirmacion"),
        "estado": compra["estado"],
        "pelicula": {"id": pelicula["id_pelicula"],
                     "Titulo": pelicula["nombre"]},
        "entrada": entradas,
        "productos": productos,
        "total": compra["total"]
    }


def listar_compras(id_usuario):
    compras = compras_repositories.obtener_compras(id_usuario)
    if not compras:
        return None, "SIN_COMPRAS"
    resultado = []
    
    for compra in compras:
        funcion = compras_repositories.obtener_funcion(compra["id_funcion"])
        pelicula = peliculas_repositories.buscar_por_id(funcion["id_pelicula"])
        entradas  = compras_repositories.obtener_entradas(compra["id_compra"])
        productos = compras_repositories.obtener_productos_compra(compra["id_compra"])
        resultado.append(construir_compra(compra, pelicula, entradas, productos))
    return resultado, None


def compra_id(id_compra, id_usuario=None):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return None, "COMPRA_INEXISTENTE"

    return compra, None

def registrar_compra(id_usuario, datos):
    # El validador ya devuelve el error armado (o None si todo esta bien)
    error = compras_validators.validar_datos(datos)
    if error is not None:
        return None, error 

    funcion = compras_repositories.obtener_funcion(datos["id_funcion"])


    if not funcion:
        return None,"FUNCION_INEXISTENTE"
    if funcion["estado"] != "programada":
        return None, "FUNCION_NO_DISPONIBLE"
    butacas_libres = compras_repositories.butacas_disponibles(funcion["id_funcion"], datos["butacas"])
    if not butacas_libres:
        return None, "BUTACA_NO_DISPONIBLE"

    productos = []
    for item in datos.get("productos", []):
        producto = compras_repositories.obtener_producto_activo(item["id_producto"])
        if not producto:
            return None, "PRODUCTO_NO_DISPONIBLE"
        productos.append((producto, item["cantidad"]))
    
    try:
        id_compra = compras_repositories.registrar_compra(id_usuario, datos, productos)
    except Exception:
        return None, "ERROR_COMPRA"
    if not id_compra:
        return None, "ERROR_COMPRA"
    return "Compra registrada con exito", None



def cancelar_compra(id_compra, id_usuario):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return "COMPRA_INEXISTENTE"
    if not compras_repositories.cancelacion_de_compra(id_compra, id_usuario):
        return "ERROR_CANCELACION"
    return None

def construir_factura(compra, usuario, entradas):
    funcion = funciones_repositories.obtener_funcion(compra["id_funcion"])
    productos = compras_repositories.obtener_productos_compra(compra["id_compra"])
    nombre_cliente = " ".join(
        parte for parte in (usuario.get("nombre"), usuario.get("apellido")) if parte
    )
    return {
        "id_compra": compra["id_compra"],
        "fecha": compra["fecha_creacion"],
        "estado": compra["estado"],
        "cliente": {
            "id": usuario.get("id_usuario", usuario.get("id")),
            "nombre": nombre_cliente,
            "apellido": usuario.get("apellido"),
            "email": usuario["email"],
        },
        "funcion": {
            "id": funcion["id_funcion"],
            "pelicula": funcion["pelicula"],
            "fecha_hora_inicio": funcion["fecha_hora_inicio"],
            "local": funcion["local"],
            "sala": funcion["numero_sala"],
        } if funcion else None,
        "entradas": entradas,
        "productos": productos,
        "total_compra": compra["total"],
    }
def obtener_factura(id_compra, id_usuario=None):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return None, "COMPRA_INEXISTENTE"
 
    usuario = usuarios_repositories.buscar_por_id(compra["id_usuario"])
    entradas = compras_repositories.obtener_entradas_factura(compra["id_compra"])

    return construir_factura(compra, usuario, entradas), None


def crear_qr_unico(id_compra, id_entrada):
    for _ in range(const.MAX_INTENTOS_QR):
        token = generar_token()
        codigo = generar_codigo_manual()
        if qr_repositories.registrar_qr(id_compra, id_entrada, "entrada", token, codigo):
            return True
    return False


def obtener_qr(id_compra, id_usuario=None):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return None, "COMPRA_INEXISTENTE"
    if compra["estado"] != "confirmada":
        return None, "COMPRA_NO_CONFIRMADA"
 
    entradas = compras_repositories.listar_entradas_confirmadas(id_compra)
    if not entradas:
        return None, "ENTRADAS_SIN_CONFIRMAR"
    resultado = []
    for entrada in entradas:
        qr = qr_repositories.obtener_qr_de_entrada(entrada["id_entrada"])
        if not qr:
            crear_qr_unico(id_compra, entrada["id_entrada"])
            qr = qr_repositories.obtener_qr_de_entrada(entrada["id_entrada"])
 
        resultado.append({
            "id_qr": qr["id_qr"],
            "id_entrada": entrada["id_entrada"],
            "tipo": qr["tipo"],
            "codigo_manual": qr["codigo_manual"],
            "estado": qr["estado"]
        })
    return resultado, None