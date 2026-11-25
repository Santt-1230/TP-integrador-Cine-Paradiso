def validar_token(token: str) -> bool:

    if not isinstance(token, str):
        return False

    token = token.strip()

    if len(token) == 64:
        return all(
            caracter in "0123456789abcdef"
            for caracter in token
        )
    if len(token) == 12:
        return all(
            caracter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            for caracter in token
        )

    return False


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