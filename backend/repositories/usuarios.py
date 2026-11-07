from db import ejecutar_consulta, ejecutar_mutacion

def crear_usuario(nombre, apellido, email, fecha_nacimiento, contrasena_hash):
    sql = """INSERT INTO usuarios (nombre, apellido, email, fecha_nacimiento, contrasena_hash, rol) VALUES (%s, %s, %s, %s, %s, %s)"""
    params = (nombre, apellido, email, fecha_nacimiento, contrasena_hash, "cliente")
    resultado = ejecutar_mutacion(sql, params)
    return resultado["id"]

def buscar_por_email(email):
    sql = "SELECT * FROM usuarios WHERE email = %s"
    filas = ejecutar_consulta(sql, (email,))
    return filas[0] if filas else None

def buscar_por_id(id_usuario):
    sql = "SELECT * FROM usuarios WHERE id_usuario = %s"
    filas = ejecutar_consulta(sql, (id_usuario,))
    return filas[0] if filas else None

def actualizar_perfil(id_usuario, nombre, apellido, email):
    sql = "UPDATE usuarios SET nombre = %s, apellido = %s, email = %s WHERE id_usuario = %s"
    ejecutar_mutacion(sql, (nombre, apellido, email, id_usuario))

def actualizar_contrasena(id_usuario, contrasena_hash):
    sql = "UPDATE usuarios SET contrasena_hash = %s WHERE id_usuario = %s"
    ejecutar_mutacion(sql, (contrasena_hash, id_usuario))

def listar_compras(id_usuario):
    sql = """SELECT id_compra, id_usuario, id_funcion, fecha_creacion, total, estado 
        FROM compras 
        WHERE id_usuario = %s AND estado IN ('confirmada', 'cancelada')
        ORDER BY fecha_creacion DESC"""
    return ejecutar_consulta(sql, (id_usuario,))

def listar_entradas(id_usuario):
    sql = """SELECT e.id_entrada, e.id_compra, e.id_funcion, e.id_butaca, b.fila, b.numero, e.estado 
        FROM entradas e 
        INNER JOIN compras c ON e.id_compra = c.id_compra 
        INNER JOIN butacas b ON e.id_butaca = b.id_butaca 
        WHERE c.id_usuario = %s"""
    return ejecutar_consulta(sql, (id_usuario,))

def listar_servicios(id_usuario):
    sql = """SELECT cp.id_compra, cp.id_producto AS id_servicio, p.nombre, cp.cantidad, cp.precio_unitario 
        FROM compra_productos cp 
        INNER JOIN compras c ON cp.id_compra = c.id_compra 
        INNER JOIN productos p ON cp.id_producto = p.id_producto 
        WHERE c.id_usuario = %s"""
    return ejecutar_consulta(sql, (id_usuario,))

def listar_peliculas_vistas(id_usuario):
    sql = """SELECT DISTINCT p.id_pelicula, p.nombre AS titulo, p.poster_url, p.duracion_min, p.clasificacion 
        FROM entradas e 
        INNER JOIN compras c ON e.id_compra = c.id_compra 
        INNER JOIN funciones f ON e.id_funcion = f.id_funcion 
        INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula 
        WHERE c.id_usuario = %s AND e.estado = 'utilizada'"""
    return ejecutar_consulta(sql, (id_usuario,))

def desactivar_usuario(id_usuario):
    sql = """UPDATE usuarios
             SET activo = FALSE, email = CONCAT('baja_', %s, '@eliminado.local')
             WHERE id_usuario = %s"""
    ejecutar_mutacion(sql, (id_usuario, id_usuario))