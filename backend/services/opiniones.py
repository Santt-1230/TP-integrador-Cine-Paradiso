from repositories import opiniones as opiniones_repository


def crear_opinion(id_usuario, texto, puntuacion, categoria=None):
    opiniones_repository.crear(id_usuario, texto.strip(), puntuacion, categoria)


def listar_opiniones():
    filas = opiniones_repository.listar()
    return [{**f, "fecha_creacion": f["fecha_creacion"].isoformat()} for f in filas]