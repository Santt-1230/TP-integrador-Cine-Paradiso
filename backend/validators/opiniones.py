def validar_texto(texto):
    if not isinstance(texto, str) or not texto.strip():
        return ("TEXTO_VACIO", "Opinión vacía", "Escribí tu opinión antes de enviarla")
    if len(texto.strip()) > 1000:
        return ("TEXTO_LARGO", "Opinión muy larga", "La opinión admite hasta 1000 caracteres")
    return None

CATEGORIAS_VALIDAS = {"cine", "servicio", "combos", "web"}


def validar_puntuacion(puntuacion):
    if isinstance(puntuacion, bool) or not isinstance(puntuacion, int) or puntuacion not in range(1, 6):
        return (
            "PUNTUACION_INVALIDA",
            "Puntuación inválida",
            "La puntuación debe ser un número entero entre 1 y 5.",
        )
    return None


def validar_categoria(categoria):
    if categoria is not None and categoria not in CATEGORIAS_VALIDAS:
        return (
            "CATEGORIA_INVALIDA",
            "Categoría inválida",
            "La categoría seleccionada no es válida.",
        )
    return None