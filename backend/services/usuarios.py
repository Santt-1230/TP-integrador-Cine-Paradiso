from werkzeug.security import generate_password_hash, check_password_hash #Importa funciones de la libreria Werkzeug para el cifrado y verificacion de contraseñas
from repositories import usuarios as usuarios_repository
from repositories import tokens as tokens_repository
import hashlib
import os #Permite interactuar con el sistema operativo y variables del entorno del servidor
import secrets #Para generar tokens o numeros aleatorios
from services import mailer #EPara armar y enviar correos electronicos

SESION_INVALIDA = ("SESION_INVALIDA","Sesion no valida", "La sesion no es valida")
EMAIL_DUPLICADO = ("EMAIL_DUPLICADO", "Email en uso", "El email que quieres usar ya esta en uso")
EMAIL_PENDIENTE = ("EMAIL_PENDIENTE", "Email pendiente", "Ese email ya tiene un registro pendiente de confirmacion. Revisa tu correo o pedi que te reenviemos el mail")
EMAIL_NO_VERIFICADO = ("EMAIL_NO_VERIFICADO", "Email sin confirmar", "Tenes que confirmar tu email antes de iniciar sesion. Revisa tu correo")
TOKEN_INVALIDO = ("TOKEN_INVALIDO", "Link invalido", "El link de confirmacion no es valido o ya vencio")
MAIL_NO_ENVIADO = ("MAIL_NO_ENVIADO", "Mail no enviado", "Tu cuenta fue creada, pero no pudimos enviar el mail de confirmacion. Pedi que te lo reenviemos")
MINUTOS_VALIDEZ_TOKEN = 15

def usuario_publico(usuario):
    user_id = usuario.get("id") or usuario.get("id_usuario")
    return {
        "id_usuario":       user_id,
        "nombre":           usuario.get("nombre", ""),
        "apellido":         usuario.get("apellido", ""),
        "email":            usuario.get("email", ""),
        "fecha_nacimiento": str(usuario["fecha_nacimiento"]),
        "rol":              usuario.get("rol", "cliente"),
        "activo":           bool(usuario.get("activo", True)),
        "email_verificado": bool(usuario.get("email_verificado", False))
    }

def hashear_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def enviar_verificacion(id_usuario, nombre, email):
    token = secrets.token_urlsafe(32)  # el token real solo viaja por mail; en la base se guarda su hash
    tokens_repository.invalidar_tokens(id_usuario, "verificar_email")  # el link anterior deja de servir
    tokens_repository.crear_token(id_usuario, "verificar_email", hashear_token(token), MINUTOS_VALIDEZ_TOKEN)

    link = f"{os.getenv('FRONTEND_URL', 'http://localhost:5001')}/verificar-email?token={token}"
    texto = (f"Hola {nombre}!\n\n"
             f"Para activar tu cuenta de Cine Paradiso confirma tu email entrando a este link "
             f"(vale {MINUTOS_VALIDEZ_TOKEN} minutos):\n{link}\n\n"
             f"Si no creaste una cuenta, ignora este mensaje.")
    return mailer.enviar_mail(email, "Confirma tu email - Cine Paradiso", texto)


def registrar_usuario(nombre, apellido, email, fecha_nacimiento, contrasena):
    email = email.lower()
    existente = usuarios_repository.buscar_por_email(email)
    if existente:
        if existente.get("email_verificado"):
            return None, EMAIL_DUPLICADO
        return None, EMAIL_PENDIENTE

    contrasena_hash = generate_password_hash(contrasena)
    id_nuevo = usuarios_repository.crear_usuario(nombre, apellido,email, fecha_nacimiento, contrasena_hash)

    if not enviar_verificacion(id_nuevo, nombre, email):
        return None, MAIL_NO_ENVIADO
    
    usuario = usuarios_repository.buscar_por_id(id_nuevo)
    return usuario_publico(usuario), None

def verificar_email(token):
    registro = tokens_repository.buscar_token_valido(hashear_token(token), "verificar_email")
    if not registro:
        return False, TOKEN_INVALIDO
    usuarios_repository.marcar_email_verificado(registro["id_usuario"])
    tokens_repository.marcar_usado(registro["id_token"])
    return True, None

def reenviar_verificacion(email):
    usuario = usuarios_repository.buscar_por_email(email.lower())
    if usuario and usuario.get("activo") and not usuario.get("email_verificado"):
        enviar_verificacion(usuario["id_usuario"], usuario["nombre"], usuario["email"])


def autenticar_usuario(email, contrasena):
    usuario = usuarios_repository.buscar_por_email(email.lower())
    hash_guardado = usuario.get("contrasena") or usuario.get("contrasena_hash") if usuario else None

    if not usuario or not hash_guardado or not check_password_hash(hash_guardado, contrasena):
        return None, ("CREDENCIALES_INVALIDAS", "Credenciales inválidas", "Email o contraseña incorrectos")

    if not usuario.get("activo", True):
        return None, ("CUENTA_DESACTIVADA", "Cuenta desactivada", "La cuenta está desactivada")

    if not usuario.get("email_verificado"):
        return None, EMAIL_NO_VERIFICADO
    
    return usuario_publico(usuario), None


def obtener_perfil(id_usuario):
    usuario = buscar_usuario_activo(id_usuario)
    if not usuario:
        return None, SESION_INVALIDA
    return usuario_publico(usuario), None


def buscar_usuario_activo(id_usuario):
    usuario = usuarios_repository.buscar_por_id(id_usuario)
    if not usuario or not usuario.get("activo", True):
        return None
    return usuario


def editar_perfil(id_usuario, nombre, apellido, email):
    usuario = buscar_usuario_activo(id_usuario)
    if not usuario:
        return None, SESION_INVALIDA

    if email is not None:
        email = email.lower()
        usuario_propuesto = usuarios_repository.buscar_por_email(email)
        id_propuesto = usuario_propuesto.get("id") or usuario_propuesto.get("id_usuario") if usuario_propuesto else None
        
        if usuario_propuesto and id_propuesto != id_usuario:
            return None, EMAIL_DUPLICADO

    nombre_a_guardar = nombre or usuario.get("nombre")
    apellido_a_guardar = apellido or usuario.get("apellido")
    email_a_guardar = email or usuario.get("email")

    usuarios_repository.actualizar_perfil(id_usuario, nombre_a_guardar, apellido_a_guardar, email_a_guardar)
    usuario_actualizado = usuarios_repository.buscar_por_id(id_usuario)

    return usuario_publico(usuario_actualizado), None


def cambiar_contrasena(id_usuario, contrasena_actual, contrasena_nueva):
    usuario = buscar_usuario_activo(id_usuario)

    if not usuario:
        return False, SESION_INVALIDA
    hash_guardado = usuario.get("contrasena") or usuario.get("contrasena_hash")
    if not hash_guardado or not check_password_hash(hash_guardado, contrasena_actual):
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

def dar_de_baja(id_usuario):
    usuario = buscar_usuario_activo(id_usuario)
    if not usuario:
        return False, SESION_INVALIDA
    usuarios_repository.desactivar_usuario(id_usuario)
    return True, None