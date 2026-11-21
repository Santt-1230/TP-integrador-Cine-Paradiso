import string

import utils as ut
from constants import (
    ENTERO_POSITIVO_MINIMO,
    CAPACIDAD_MAXIMA,
    ERROR_CODE_INVALID_PARAMETER,
    BUTACAS_POR_FILA
)


CAMPOS_EDITABLES = ('numero_sala', 'estado', 'letras', 'cantidades')


def validar_id_local(id_local) -> int:
    return ut.validar_entero_positivo(
        id_local, ENTERO_POSITIVO_MINIMO, 'id_local'
    )


def validar_filtro_local(id_local) -> int | None:
    if id_local is None or id_local == '':
        return None
    return validar_id_local(id_local)


def validar_id_sala(id_sala) -> int:
    return ut.validar_entero_positivo(
        id_sala, ENTERO_POSITIVO_MINIMO, 'id_sala'
    )


def validar_numero_sala(numero_sala) -> int:
    return ut.validar_entero_positivo(
        numero_sala, ENTERO_POSITIVO_MINIMO, 'numero_sala'
    )

def validar_estado(estado) -> str:
    if not isinstance(estado, str) or estado not in ('activa', 'inactiva'):
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Estado invalido',
            description='El estado debe ser activa o inactiva'
        ))

    return estado


def validar_filtro_estado(estado) -> str | None:
    if estado is None or estado == '' or estado == 'todas':
        return None
    return validar_estado(estado)


def error_filas(descripcion):
    return ValueError(ut.construir_error_api(
        code=ERROR_CODE_INVALID_PARAMETER,
        message='Filas invalidas',
        description=descripcion
    ))


def error_datos(descripcion):
    return ValueError(ut.construir_error_api(
        code=ERROR_CODE_INVALID_PARAMETER,
        message='Datos invalidos',
        description=descripcion
    ))


def validar_letras(letras) -> list:
    if not isinstance(letras, list) or not letras:
        raise error_filas('Ingresa al menos una fila')

    if len(letras) > len(string.ascii_uppercase):
        raise error_filas(
            f'La sala no puede tener mas de {len(string.ascii_uppercase)} filas'
        )

    letras_validas = []
    vistas = set()

    for letra in letras:
        if isinstance(letra, str):
            letra = letra.strip().upper()

        if not isinstance(letra, str) or len(letra) != 1 or letra not in string.ascii_uppercase:
            raise error_filas('La fila debe ser una letra de la A a la Z')

        if letra in vistas:
            raise error_filas(f"La fila '{letra}' esta repetida")

        vistas.add(letra)
        letras_validas.append(letra)

    return letras_validas


def validar_cantidades_filas(cantidades) -> list:
    if not isinstance(cantidades, list) or not cantidades:
        raise error_filas('Ingresa al menos una fila')

    if len(cantidades) > len(string.ascii_uppercase):
        raise error_filas(
            f'La sala no puede tener mas de {len(string.ascii_uppercase)} filas'
        )

    cantidades_validas = []
    total = 0

    for cantidad in cantidades:
        cantidad = ut.validar_entero_positivo(
            cantidad, ENTERO_POSITIVO_MINIMO, 'cantidad'
        )

        if cantidad > BUTACAS_POR_FILA:
            raise error_filas(
                f'Cada fila puede tener hasta {BUTACAS_POR_FILA} butacas'
            )

        total += cantidad
        cantidades_validas.append(cantidad)

    if total > CAPACIDAD_MAXIMA:
        raise error_filas(
            f'La sala no puede superar las {CAPACIDAD_MAXIMA} butacas'
        )

    return cantidades_validas


def validar_filas(letras, cantidades) -> list:
    letras_validas = validar_letras(letras)
    cantidades_validas = validar_cantidades_filas(cantidades)

    if len(letras_validas) != len(cantidades_validas):
        raise error_filas('Cada fila debe tener letra y cantidad')

    return [{'fila': l, 'cantidad': c}
            for l, c in zip(letras_validas, cantidades_validas)]


def validar_creacion_sala(datos):
    if not isinstance(datos, dict):
        raise error_datos('Los datos de la sala son obligatorios')

    for campo in ('id_local', 'numero_sala', 'letras', 'cantidades'):
        if campo not in datos:
            raise error_datos(f"Falta el campo '{campo}'")

    return {
        'id_local': validar_id_local(datos['id_local']),
        'numero_sala': validar_numero_sala(datos['numero_sala']),
        'filas': validar_filas(datos['letras'], datos['cantidades']),
    }


def validar_actualizacion_sala(datos):
    if not isinstance(datos, dict) or not datos:
        raise error_datos('Ingrese numero_sala, estado, letras y cantidades')

    for campo in datos:
        if campo not in CAMPOS_EDITABLES:
            raise error_datos(f"No se puede modificar el campo '{campo}'")

    if ('letras' in datos) != ('cantidades' in datos):
        raise error_datos('Las letras y las cantidades se envian juntas')

    cambios = {}

    if 'numero_sala' in datos:
        cambios['numero_sala'] = validar_numero_sala(datos['numero_sala'])

    if 'estado' in datos:
        cambios['estado'] = validar_estado(datos['estado'])

    if 'letras' in datos:
        cambios['filas'] = validar_filas(datos['letras'], datos['cantidades'])

    return cambios