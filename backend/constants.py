import os
from dotenv import load_dotenv

load_dotenv()

ENTERO_POSITIVO_MINIMO = 1
BUTACAS_POR_FILA = 20

ERROR_MESSAGE_DATABASE_ERROR = 'No se pudo completar la operacion por un problema con la base de datos'
ERROR_DESCRIPTION_DATABASE_ERROR = 'Ocurrio un problema al consultar la base de datos'
ERROR_CODE_INVALID_PARAMETER = 'invalid.parameter'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_EMPTY_VALUE = 'empty.value'
ERROR_CODE_DATABASE_ERROR = 'database.error'
ERROR_CODE_SALA_NOT_FOUND = 'sala.not_found'
ERROR_CODE_LOCAL_NOT_FOUND = 'local.not_found'
ERROR_CODE_LOCAL_INACTIVE = 'local.inactive'
ERROR_CODE_SALA_CONFLICT = 'sala.conflict'
