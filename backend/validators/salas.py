import utils as ut
from constants import (
    ENTERO_POSITIVO_MINIMO, 
    CAPACIDAD_MAXIMA, 
    ERROR_CODE_INVALID_PARAMETER, 
    BUTACAS_POR_FILA)
import string

CAMPOS_EDITABLES = ('numero_sala', 'estado', 'letras', 'cantidades')
def validar_id_local(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Parametro invalido',
            description="id_local debe ser un numero entero."
        ))

def validar_id_sala(id_sala)->int:
    return ut.validar_entero_positivo(
        id_sala, ENTERO_POSITIVO_MINIMO, 'id_sala'
    )

def validar_numero_sala(numero_sala)->int:
    return ut.validar_entero_positivo(
        numero_sala, ENTERO_POSITIVO_MINIMO, 'numero_sala'
        )

def validar_capacidad(capacidad)->int:
    capacidad = ut.validar_entero_positivo(
        capacidad, ENTERO_POSITIVO_MINIMO, 'capacidad'
    )
    if capacidad > CAPACIDAD_MAXIMA:
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Capacidad invalida',
            description=f'La capacidad no puede superar {CAPACIDAD_MAXIMA} butacas'
        ))

    return capacidad

def validar_estado(estado)->str:
    if estado not in ('activa', 'inactiva'):
        raise ValueError(ut.construir_error_api(
            code=ERROR_CODE_INVALID_PARAMETER,
            message='Estado invalido',
            description='El estado debe ser activa o inactiva'
        ))
    return estado

def validar_filtro_estado(estado)->str:
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


def validar_filas(filas) -> list:
    if not isinstance(filas, list) or not filas:
        raise error_filas('Ingresa al menos una fila')

    resultado = []
    total = 0
    vistas = set()

    for item in filas:
        if not isinstance(item, dict):
            raise error_filas('Cada fila debe tener letra y cantidad')

        fila = item.get('fila')
        if isinstance(fila, str):
            fila = fila.strip().upper()
        if not isinstance(fila, str) or len(fila) != 1 or fila not in string.ascii_uppercase:
            raise error_filas('La fila debe ser una letra de la A a la Z')
        if fila in vistas:
            raise error_filas(f"La fila '{fila}' esta repetida")
        vistas.add(fila)

        cantidad = ut.validar_entero_positivo(
            item.get('cantidad'), ENTERO_POSITIVO_MINIMO, 'cantidad')
        if cantidad > BUTACAS_POR_FILA:
            raise error_filas(f'Cada fila puede tener hasta {BUTACAS_POR_FILA} butacas')

        total += cantidad
        resultado.append({'fila': fila, 'cantidad': cantidad})

    if total > CAPACIDAD_MAXIMA:
        raise error_filas(f'La sala no puede superar las {CAPACIDAD_MAXIMA} butacas')

    return sorted(resultado, key=lambda f: f['fila'])

def armar_filas(letras, cantidades)->list:
    if not isinstance(letras, list) or not isinstance(cantidades,list) or not letras:
        raise error_filas('Ingrese al menos una fila')
    if len(letras) != len(cantidades):
        raise error_filas('Cada fila debe tener letra y cantidad')
    return [{'fila':l, 'cantidad':c} for l, c in zip(letras, cantidades)]

def validar_cantidades_filas(cantidades) -> list:
    if not isinstance(cantidades, list) or not cantidades:
        raise error_filas('Ingresa al menos una fila')
    if len(cantidades) > len(string.ascii_uppercase):
        raise error_filas(f'La sala no puede tener mas de {len(string.ascii_uppercase)} filas')

    filas = [
        {'fila': string.ascii_uppercase[i],
         'cantidad': ut.validar_entero_positivo(c, ENTERO_POSITIVO_MINIMO, 'cantidad')}
        for i, c in enumerate(cantidades)
    ]
    return validar_filas(filas)

def validar_creacion_sala(datos):
    if not isinstance(datos, dict):
        raise error_datos('Los datos de la sala son obligatorios')

    for campo in ('id_local', 'numero_sala', 'letras', 'cantidades'):
        if campo not in datos:
            raise error_datos(f"Falta el campo '{campo}'")

    return {
        'id_local': ut.validar_entero_positivo(
            datos['id_local'], ENTERO_POSITIVO_MINIMO, 'id_local'
        ),
        'numero_sala': validar_numero_sala(datos['numero_sala']),
        'filas': validar_filas(armar_filas(datos['letras'], datos['cantidades'])),
    }

def validar_actualizacion_sala(datos):
    if not isinstance(datos, dict) or not datos:
        raise error_datos('Ingrese numero_sala, estado, letras o cantidades')
    for campo in datos:
        if campo not in CAMPOS_EDITABLES:
            raise error_datos(f"No se puede modificar el campo '{campo}'")
    cambios = {}
    if 'numero_sala' in datos:
        cambios['numero_sala'] = validar_numero_sala(datos['numero_sala'])
    if 'estado' in datos:
        cambios['estado'] = validar_estado(datos['estado'])
    if 'letras' in datos or 'cantidades' in datos:
        cambios['filas'] = validar_filas(armar_filas(
            datos.get('letras'), datos.get('cantidades'))
            )
        
    return cambios

