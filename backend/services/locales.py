from repositories import locales as locales_repository

def listar_locales():
    return locales_repository.listar_locales_activos()