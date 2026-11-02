import os
from dotenv import load_dotenv

load_dotenv()

ENTERO_POSITIVO_MINIMO = 1
ERROR_CODE_INVALID_PARAMETER = 'invalid.parameter'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_EMPTY_VALUE = 'empty.value'
ERROR_CODE_DATABASE_ERROR = 'database.error'

ERROR_CODE_NOT_FOUND = 'not.found'
ERROR_CODE_DUPLICATE = 'duplicate.resource'
ERROR_CODE_FORBIDDEN = 'forbidden'
ERROR_CODE_EXTERNAL_SERVICE = 'external.service.error'

ROL_ADMINISTRADOR = 'administrador'
