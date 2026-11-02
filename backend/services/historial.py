from repositories import historial as historial_repository

def obtener_historial(id_usuario):
    filas = historial_repository.obtener_por_usuario(id_usuario)
    return [
        {
            **fila,
            "total": float(fila["total"]),
            "monto_reembolsado": float(fila["monto_reembolsado"] or 0),
            "fecha_creacion": fila["fecha_creacion"].isoformat(),
            "fecha_hora_inicio": fila["fecha_hora_inicio"].isoformat(),
        }
        for fila in filas
    ]