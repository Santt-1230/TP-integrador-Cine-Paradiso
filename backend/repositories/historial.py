from utils_db import ejecutar_consulta

def obtener_por_usuario(id_usuario):
    sql_historial = """
    SELECT c.id_compra, c.estado, c.total, c.fecha_creacion,
           c.monto_reembolsado, f.fecha_hora_inicio,
           p.titulo AS pelicula, l.nombre AS local, s.numero_sala,
           GROUP_CONCAT(CONCAT(b.fila, b.numero)
                        ORDER BY b.fila, b.numero SEPARATOR ', ') AS butacas
    FROM compras c
    JOIN funciones f ON f.id_funcion = c.id_funcion
    JOIN peliculas p ON p.id_pelicula = f.id_pelicula
    JOIN salas s ON s.id_sala = f.id_sala
    JOIN locales l ON l.id_local = s.id_local
    LEFT JOIN entradas e ON e.id_compra = c.id_compra
    LEFT JOIN butacas b ON b.id_butaca = e.id_butaca
    WHERE c.id_usuario = %s AND c.estado IN ('confirmada', 'cancelada')
    GROUP BY c.id_compra, c.estado, c.total, c.fecha_creacion,
             c.monto_reembolsado, f.fecha_hora_inicio,
             p.titulo, l.nombre, s.numero_sala
    ORDER BY f.fecha_hora_inicio DESC
"""

    return ejecutar_consulta(sql_historial, (id_usuario,))