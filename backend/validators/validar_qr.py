
def validar_token(token: str) -> bool:

    if not isinstance(token, str):
        return False

    if len(token) != 64:
        return False

    for caracter in token:
        if caracter not in "0123456789abcdef":
            return False

    return True