from flask import jsonify

def construir_error_api(code:str, message:str, description:str, level:str = 'error')->dict:
    return {
        'errors' :[{
            "error" : level,
            "code" : code,
            "message" : message,
            "description" : description
        }]
    }
