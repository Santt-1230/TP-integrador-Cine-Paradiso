import os
from dotenv import load_dotenv
import string
load_dotenv()

ENTERO_POSITIVO_MINIMO = 1
MINUTOS_ENTRE_FUNCIONES = 30
ERROR_CODE_INVALID_PARAMETER = 'invalid.parameter'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_EMPTY_VALUE = 'empty.value'
ERROR_CODE_DATABASE_ERROR = 'database.error'
ALFABETO_CODIGO = string.ascii_uppercase + string.digits
MAX_INTENTOS_QR = 5