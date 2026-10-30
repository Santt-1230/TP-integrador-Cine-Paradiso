from datetime import datetime


def texto(datos, clave):
    valor = datos.get(clave)
    return valor if isinstance(valor, str) else ""


def error_validacion(descripcion):
    return ("DATOS_INVALIDOS", "Datos invalidos", descripcion)


def validar_nombre(nombre):
    if nombre == "" or len(nombre) > 150:
        return error_validacion("El nombre es obligatorio y tiene un maximo de 150 caracteres")
    return None


def validar_apellido(apellido):
    if apellido == "" or len(apellido) > 150:
            return error_validacion("El apellido es obligatorio y tiene un maximo de 150 caracteres")
    return None 

def validar_email(email):
    if "@" not in email or "." not in email or len(email) > 200:
        return error_validacion("El email ingresado no es valido")
    return None

def validar_fecha_nacimiento(fecha_nacimiento):
    if not fecha_nacimiento:
        return error_validacion("La fecha de nacimiento es obligatoria")
    try:
        datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
    except ValueError:
        return error_validacion("La fecha de nacimiento debe tener formato YYYY-MM-DD")
    return None


def validar_contrasena(contrasena, repetir_contrasena):
    if len(contrasena) < 8:
        return error_validacion("La contraseña debe contener al menos 8 caracteres")
    if not repetir_contrasena:
        return error_validacion("Confirrmar/Repetir la contraseña es obligatorio")
    if contrasena != repetir_contrasena:
        return error_validacion("Las contraseñas no coinciden")   
    
    return None


def validar_registro(datos):
    if not isinstance(datos, dict):
        return error_validacion("Faltan los datos del usuario")

    nombre = texto(datos, "nombre").strip()
    apellido = texto(datos, "apellido").strip()
    email = texto(datos, "email").strip()
    fecha_nacimiento = texto(datos,"fecha_nacimiento").strip()
    contrasena = texto(datos, "contrasena") #si la contraseña viene vacia, entonces --> datos, "" y luego len("") = 0
    repetir_contrasena = texto(datos,"repetir_contrasena")
    
    return (validar_nombre(nombre) or validar_apellido(apellido) or validar_email(email) 
            or validar_fecha_nacimiento(fecha_nacimiento) or validar_contrasena(contrasena, repetir_contrasena))


def validar_login(datos):
    if not isinstance(datos, dict):
        return error_validacion("Faltan ingresar los datos para acceder")

    if texto(datos, "email").strip() == "" or texto(datos, "contrasena") == "":
        return error_validacion("Completar los campos de email y contraseña son obligatorios")

    return None