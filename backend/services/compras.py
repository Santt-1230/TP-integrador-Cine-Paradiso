from repositories import compras as compras_repositories
from repositories import usuarios as usuarios_repositories
from validators import compras as compras_validators
from repositories import qr as qr_repositories
from repositories import peliculas as peliculas_repositories
from repositories import salas as salas_repositories 
from repositories import locales as locales_repositories
import constants as const
import secrets

def generar_token():
    return secrets.token_hex(32)

def generar_codigo_manual():
    return "".join(secrets.choice(const.ALFABETO_CODIGO) for _ in range(12))


def construir_compra(compra, pelicula, entradas, productos):
    compra = {
        "id": compra["id_compra"],
        "fecha": compra["fecha_creacion"],
        "fecha_confirmacion": compra.get("fecha_confirmacion"),
        "estado": compra["estado"],
        "pelicula": {"id": pelicula["id_pelicula"],
                     "titulo": pelicula["nombre"],
                     "imagen_url": pelicula["poster_url"]},
        "entrada": [],
        "productos": productos,
        "total": compra["total"]
    }
    for entrada in entradas:
        butaca = compras_repositories.butacas_id(entrada["id_butaca"])
        entrada_dict = {
            "id_entrada": entrada["id_entrada"],
            "fila": butaca["fila"],
            "numero": butaca["numero"],
            "estado": entrada["estado"]
        }
        compra["entrada"].append(entrada_dict)
    return compra


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
    funcion = compras_repositories.obtener_funcion(compra["id_funcion"])
    pelicula = peliculas_repositories.buscar_por_id(funcion["id_pelicula"])
    entradas  = compras_repositories.obtener_entradas(compra["id_compra"])
    productos = compras_repositories.obtener_productos_compra(compra["id_compra"])

    return construir_compra(compra,pelicula,entradas,productos), None

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
    estado_butacas = compras_repositories.butacas_disponibles(
        funcion["id_funcion"], datos["butacas"]
    )
    if estado_butacas == "inexistentes":
        return None, "BUTACA_INEXISTENTE"
    if estado_butacas == "inactivas":
        return None, "BUTACA_INACTIVA"
    if estado_butacas != "disponibles":
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
    return id_compra , None



def cancelar_compra(id_compra, id_usuario):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return "COMPRA_INEXISTENTE"
    if not compras_repositories.cancelacion_de_compra(id_compra, id_usuario):
        return "ERROR_CANCELACION"
    return None

def construir_factura(compra, cliente, funcion, entradas, productos, sala, pelicula, local):
    subtotal_entradas = sum(entrada["precio_unitario"] for entrada in entradas)

    subtotal_productos = sum(producto["precio_unitario"] * producto["cantidad"] for producto in productos)

    total = subtotal_entradas + subtotal_productos

    return {
        "factura": {
            "numero": compra["numero_factura"],
            "id_compra": compra["id_compra"],
            "fecha_emision": compra["fecha_confirmacion"],
            "estado": compra["estado"],
            "moneda": "ARS"
        },

        "cliente": {
            "id_usuario": cliente["id_usuario"],
            "nombre": f"{cliente['nombre']} {cliente['apellido']}",
            "nombre_pila": cliente["nombre"],
            "apellido": cliente["apellido"],
            "email": cliente["email"]
        },

        "funcion": {
            "id_funcion": funcion["id_funcion"],
            "pelicula": pelicula["nombre"],
            "id_pelicula": funcion["id_pelicula"],
            "fecha_hora_inicio": funcion["fecha_hora_inicio"],
            "local": local["nombre"],
            "id_local": sala["id_local"],
            "sala": sala["id_sala"]
        },

        "entradas": [
            {
                "id_entrada": entrada["id_entrada"],
                "fila": entrada["fila"],
                "numero": entrada["numero"],
                "precio_unitario": entrada["precio_unitario"]
            }
            for entrada in entradas
        ],

        "productos": [
            {
                "id_producto": producto["id_producto"],
                "nombre": producto["nombre"],
                "cantidad": producto["cantidad"],
                "precio_unitario": producto["precio_unitario"],
                "subtotal": producto["precio_unitario"] * producto["cantidad"]
            }
            for producto in productos
        ],

        "totales": {
            "subtotal_entradas": subtotal_entradas,
            "subtotal_productos": subtotal_productos,
            "total": total
        }
    }
def obtener_factura(id_compra, id_usuario=None):
    compra = compras_repositories.obtener_compra_id(id_compra, id_usuario)
    if not compra:
        return None, "COMPRA_INEXISTENTE"
 
    cliente = usuarios_repositories.buscar_por_id(compra["id_usuario"])
    entradas = compras_repositories.obtener_entradas_factura(compra["id_compra"])
    productos = compras_repositories.obtener_productos_compra(compra["id_compra"])
    funcion = compras_repositories.obtener_funcion(compra["id_funcion"])
    sala = salas_repositories.listar_sala_por_id(funcion["id_sala"])
    pelicula = peliculas_repositories.buscar_por_id(funcion["id_pelicula"])
    local = locales_repositories.obtener_local_id(sala["id_local"])
    lista_entradas = []
    for entrada_nv in entradas:
        butaca = compras_repositories.butacas_id(entrada_nv["id_butaca"])
        entradas_dict = {
            "id_entrada": entrada_nv["id_entrada"],
            "fila": butaca["fila"],
            "numero": butaca["numero"],
            "precio_unitario": entrada_nv["precio_unitario"]
        }
        lista_entradas.append(entradas_dict)
    return construir_factura(
        compra, cliente, funcion, lista_entradas, productos, sala, pelicula, local
    ), None


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
            "estado": qr["estado"],
            "token": qr["token"]
        })
    return resultado, None