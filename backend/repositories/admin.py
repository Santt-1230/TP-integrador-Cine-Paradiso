from db import obtener_conexion


def obtener_usuarios():
    
    try: 
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""SELECT id_usuario, nombre, email, rol FROM usuario""") #No agrego contrasena por temas de seguridad

        usuarios = cursor.fetchall() #.fetchall se utiliza para recuperar todas las filas restantes del resultado de una consulta SQL ejecutada previamente


    finally:
        cursor.close()
        conexion.close()

    return usuarios