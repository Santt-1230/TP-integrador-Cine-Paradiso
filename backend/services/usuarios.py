from werkzeug.security import generate_password_hash, check_password_hash #Importa funciones de la libreria Werkzeug para el cifrado y verificacion de contraseñas
from repositories import usuarios as usuarios_repository

SESION_INVALIDA = ("SESION_INVALIDA","Sesion no valida", "La sesion no es valida")
EMAIL_DUPLICADO = ("EMAIL_DUPLICADO", "Email en uso", "El email que quieres usar ya esta en uso")

def usuario_publico(usuario):
    return {
        "id_usuario":         usuario["id_usuario"],
        "nombre":             usuario["nombre"],
        "apellido":           usuario["apellido"],
        "email":              usuario["email"],
        "fecha_nacimiento":   str(usuario["fecha_nacimiento"]), #2007-04-20
        "rol":                usuario["rol"],
        "activo":             bool(usuario["activo"]),
    }


def registrar_usuario(nombre, apellido, email, fecha_nacimiento, contrasena):
    email = email.lower()

    if usuarios_repository.buscar_por_email(email):
        return None, EMAIL_DUPLICADO

    contrasena_hash = generate_password_hash(contrasena)
    id_nuevo = usuarios_repository.crear_usuario(nombre, apellido,email, fecha_nacimiento, contrasena_hash)
    usuario = usuarios_repository.buscar_por_id(id_nuevo)

    return usuario_publico(usuario), None


def autenticar_usuario(email, contrasena):
    usuario = usuarios_repository.buscar_por_email(email.lower())

    if not usuario or not check_password_hash(usuario["contrasena_hash"], contrasena):
        return None, ("CREDENCIALES_INVALIDAS","Credenciales invalidas","Email o contraseña incorrectos")

    if not usuario["activo"]:
        return None, ("CUENTA_DESACTIVADA","Cuenta desactivada", "La cuenta está desactivada")

    return usuario_publico(usuario), None


def obtener_perfil(id_usuario):
    usuario = buscar_usuario_activo(id_usuario)
    if not usuario:
        return None, SESION_INVALIDA
    return usuario_publico(usuario), None


def buscar_usuario_activo(id_usuario):
    usuario = usuarios_repository.buscar_por_id(id_usuario)
    if not usuario or not usuario["activo"]:
        return None
    return usuario


def editar_perfil(id_usuario, nombre, apellido, email):
    usuario = buscar_usuario_activo(id_usuario)
    if not usuario:
        return None, SESION_INVALIDA

    if email is not None:
        email = email.lower()
        usuario_propuesto = usuarios_repository.buscar_por_email(email)
        if usuario_propuesto and usuario_propuesto["id_usuario"] != id_usuario:
            return None, EMAIL_DUPLICADO 

    nombre_a_guardar = nombre or usuario["nombre"]
    apellido_a_guardar = apellido or usuario["apellido"]
    email_a_guardar = email or usuario["email"]

    usuarios_repository.actualizar_perfil(id_usuario, nombre_a_guardar, apellido_a_guardar, email_a_guardar)
    usuario_actualizado = usuarios_repository.buscar_por_id(id_usuario)
    return usuario_publico(usuario_actualizado), None


def cambiar_contrasena(id_usuario, contrasena_actual, contrasena_nueva):
    usuario = buscar_usuario_activo(id_usuario)

    if not usuario:
        return False, SESION_INVALIDA
    if not check_password_hash(usuario["contrasena_hash"], contrasena_actual): #Si la contraseña (hasheada) no coincide con la contraseña ingresada
        return False, ("CONTRASENA_INCORRECTA", "Contraseña incorrecta", "la contraseña ingresada no es correcta")

    usuarios_repository.actualizar_contrasena(id_usuario, generate_password_hash(contrasena_nueva))
    return True, None

ESTADOS_ENTRADA = {"reservada": "activa", "confirmada": "activa", "utilizada": "utilizada", "cancelada": "cancelada"}
def entrada_publica(entrada):
    return {
        "id_entrada": entrada["id_entrada"],
        "id_butaca":  entrada["id_butaca"],
        "fila":       entrada["fila"],
        "numero":     entrada["numero"],
        "estado":     ESTADOS_ENTRADA[entrada["estado"]],}


def servicio_publico(servicio):
    return {
        "id_servicio":     servicio["id_servicio"],
        "nombre":          servicio["nombre"],
        "cantidad":        servicio["cantidad"],
        "precio_unitario": float(servicio["precio_unitario"]),}


def obtener_historial(id_usuario):
    usuario = buscar_usuario_activo(id_usuario)

    if not usuario:
        return None, SESION_INVALIDA

    compras = usuarios_repository.listar_compras(id_usuario)
    entradas = usuarios_repository.listar_entradas(id_usuario)
    servicios = usuarios_repository.listar_servicios(id_usuario)

    historial_compras = []
    for compra in compras:
        historial_compras.append({
            "id_compra":  compra["id_compra"],
            "id_usuario": compra["id_usuario"],
            "id_funcion": compra["id_funcion"],
            "fecha_hora": str(compra["fecha_creacion"]),
            "total":      float(compra["total"]),
            "estado":     compra["estado"],
            "entradas":   [entrada_publica(e) for e in entradas if e["id_compra"] == compra["id_compra"]],
            "servicios":  [servicio_publico(s) for s in servicios if s["id_compra"] == compra["id_compra"]],
        })

    peliculas_vistas = usuarios_repository.listar_peliculas_vistas(id_usuario)
    return {"compras": historial_compras, "peliculas_vistas": peliculas_vistas}, None