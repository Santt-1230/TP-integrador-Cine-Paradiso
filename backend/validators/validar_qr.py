

def validar_token(token: str) -> bool:

    if not isinstance(token, str):
        return False

    if len(token) != 64:
        return False

    for caracter in token:
        if caracter not in "0123456789abcdef":
            return False

    return True


def validar_categoria(categoria: str) -> bool:

    if not isinstance(categoria, str):
        return False

    categorias_validas = {
        "bebida",
        "comida",
        "estacionamiento",
        "vip"
    }

    return categoria in categorias_validas
