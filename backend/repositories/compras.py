from db import ejecutar_consulta, ejecutar_mutacion, transaccion
from datetime import datetime
from repositories import qr as qr_repositories


def obtener_compras(id):
    sql = "SELECT * FROM compras WHERE id_usuario = %s;"
    params = [id]
    compras = ejecutar_consulta(sql, params)
    return compras


def obtener_compra_id(id_compra, id_usuario):
    sql = "SELECT * FROM compras WHERE id_compra = %s"
    parametros = [id_compra]
    if id_usuario is not None:
        sql += " AND id_usuario = %s"
        parametros.append(id_usuario)
    compra = ejecutar_consulta(sql, parametros)
    return  compra[0] if compra else None

#validar que la butaca este activa, o libre, y agregar datos a la base de butacas
def generar_numero_factura(id_compra):
    anio = datetime.now().year
    return f"FAC-{anio}-{id_compra:06d}"


def registrar_compra(id_usuario, datos, productos):
    with transaccion() as cursor:

        # Obtener el precio de las entradas
        cursor.execute(
            "SELECT precio_entrada FROM funciones WHERE id_funcion = %s",
            (datos["id_funcion"],),
        )

        funcion = cursor.fetchone()

        if not funcion:
            raise ValueError("La función dejó de existir al registrar la compra")

        precio_entrada = funcion["precio_entrada"]
        total = precio_entrada * len(datos["butacas"])

        # Registrar la compra
        cursor.execute(
            "INSERT INTO compras "
            "(id_usuario, id_funcion, estado, total, expira_en, fecha_confirmacion) "
            "VALUES (%s, %s, 'confirmada', %s, NOW(), NOW())",
            (id_usuario, datos["id_funcion"], total),
        )

        id_compra = cursor.lastrowid

        # Registrar las entradas
        for id_butaca in datos["butacas"]:

            cursor.execute(
                "INSERT INTO entradas "
                "(id_compra, id_funcion, id_butaca, precio_unitario, estado) "
                "VALUES (%s, %s, %s, %s, 'confirmada')",
                (id_compra, datos["id_funcion"], id_butaca, precio_entrada),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo registrar una entrada")

        # Registrar productos y generar un QR por cada producto
        for item in productos:

            producto = item["producto"]
            cantidad = item["cantidad"]

            # Registrar el producto con su cantidad total
            cursor.execute(
                "INSERT INTO compra_productos "
                "(id_compra, id_producto, cantidad, precio_unitario) "
                "VALUES (%s, %s, %s, %s)",
                (
                    id_compra,
                    producto["id_producto"],
                    cantidad,
                    producto["precio"]
                ),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo agregar un producto a la compra")

            # Obtener el identificador del producto comprado
            id_compra_producto = cursor.lastrowid

            # Registrar el QR del producto
            qr_registrado = False

            for token, codigo in item["qrs"]:

                if not qr_registrado:
                    qr_registrado = qr_repositories.registrar_qr_producto(
                        cursor,
                        id_compra,
                        id_compra_producto,
                        token,
                        codigo
                    )

            if not qr_registrado:
                raise RuntimeError("No se pudo generar el QR del producto")

            # Actualizar el total
            cursor.execute(
                "UPDATE compras SET total = total + %s WHERE id_compra = %s",
                (producto["precio"] * cantidad, id_compra),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo actualizar el total de la compra")
        # Generar el número de factura
        numero_factura = generar_numero_factura(id_compra)

        cursor.execute(
            "UPDATE compras SET numero_factura = %s WHERE id_compra = %s",
            (numero_factura, id_compra),
        )

        if cursor.rowcount != 1:
            raise RuntimeError("No se pudo asignar el número de factura")

        return id_compra

def butacas_disponibles(id_funcion, id_butacas):
    if not id_butacas:
        return False

    butacas = tuple(dict.fromkeys(int(butaca) for butaca in id_butacas))
    marcadores = ", ".join(["%s"] * len(butacas))
    sql = (
        "SELECT COUNT(DISTINCT b.id_butaca) AS butacas_validas, "
        "COUNT(DISTINCT CASE WHEN c.id_compra IS NOT NULL "
        "THEN b.id_butaca END) AS butacas_ocupadas "
        "FROM funciones f "
        "INNER JOIN butacas b ON b.id_sala = f.id_sala "
        "LEFT JOIN entradas e ON e.id_funcion = f.id_funcion "
        "AND e.id_butaca = b.id_butaca "
        "AND e.estado IN ('reservada', 'confirmada', 'utilizada') "
        "LEFT JOIN compras c ON c.id_compra = e.id_compra "
        "AND (c.estado = 'confirmada' OR "
        "(c.estado = 'pendiente' AND c.expira_en > NOW())) "
        f"WHERE f.id_funcion = %s AND b.id_butaca IN ({marcadores})"
    )
    resultado = ejecutar_consulta(sql, (id_funcion, *butacas))
    if not resultado:
        return False
    return (
        resultado[0]["butacas_validas"] == len(butacas)
        and resultado[0]["butacas_ocupadas"] == 0
    )

def obtener_funcion_precio(id_funcion):
    sql = "SELECT precio_entrada from funciones WHERE id_funcion = %s"
    parametros = [id_funcion]
    precio_unitario = ejecutar_consulta(sql, parametros)
    return precio_unitario[0] if precio_unitario else None


def cancelacion_de_compra(id_compra, id_usuario):
    sql = "UPDATE compras SET estado = 'cancelada', fecha_cancelacion = NOW()  WHERE id_compra = %s AND id_usuario = %s AND (estado = 'confirmada' OR estado = 'pendiente')"
    parametros = [id_compra, id_usuario]
    print (parametros)
    cambiar = ejecutar_mutacion(sql, parametros)
    return cambiar["filas"] > 0

def obtener_entradas(id_compra):
    sql = "SELECT * FROM entradas WHERE id_compra = %s"
    parametros = [id_compra]
    entradas = ejecutar_consulta(sql, parametros)
    return entradas


def obtener_entradas_factura(id_compra):
    sql = (
        "SELECT e.id_entrada, e.id_funcion, e.id_butaca, b.fila, b.numero, "
        "e.precio_unitario, e.estado "
        "FROM entradas e INNER JOIN butacas b ON b.id_butaca = e.id_butaca "
        "WHERE e.id_compra = %s ORDER BY e.id_entrada"
    )
    return ejecutar_consulta(sql, (id_compra,))


def obtener_productos_compra(id_compra):
    sql = (
        "SELECT cp.id_producto, p.nombre, cp.cantidad, cp.precio_unitario "
        "FROM compra_productos cp "
        "INNER JOIN productos p ON p.id_producto = cp.id_producto "
        "WHERE cp.id_compra = %s ORDER BY cp.id_producto"
    )
    return ejecutar_consulta(sql, (id_compra,))


def listar_entradas_confirmadas(id_compra):
    sql = "SELECT id_entrada FROM entradas WHERE id_compra = %s AND estado = 'confirmada'"
    parametros = [id_compra]
    return ejecutar_consulta(sql, parametros)

def obtener_funcion(id_funcion):
    sql = "SELECT * FROM funciones WHERE id_funcion = %s"
    parametros = [id_funcion]
    funcion = ejecutar_consulta(sql, parametros)
    return funcion[0] if funcion else None


def obtener_producto_activo(id_producto):
    filas = ejecutar_consulta(
        "SELECT id_producto, nombre, precio FROM productos "
        "WHERE id_producto = %s AND activo = TRUE",
        (id_producto,),
    )
    return filas[0] if filas else None


def insertar_servicio_compra(id_compra, id_producto, cantidad, precio):
    return ejecutar_mutacion(
        "INSERT INTO compra_productos "
        "(id_compra, id_producto, cantidad, precio_unitario) "
        "VALUES (%s, %s, %s, %s)",
        (id_compra, id_producto, cantidad, precio),
    )


def actualizar_total_compra(id_compra, subtotal):
    ejecutar_mutacion(
        "UPDATE compras SET total = total + %s WHERE id_compra = %s",
        (subtotal, id_compra),
    )
    filas = ejecutar_consulta(
        "SELECT total FROM compras WHERE id_compra = %s", (id_compra,)
    )
    return filas[0]["total"] if filas else None

def butacas_id(id_butaca):
    butaca = ejecutar_consulta(
        "SELECT * FROM butacas WHERE id_butaca = %s",
        (id_butaca,)
    )
    return butaca[0] if butaca else None

