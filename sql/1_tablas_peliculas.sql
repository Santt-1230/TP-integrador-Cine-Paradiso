
-- Re-ejecutable: IF NOT EXISTS no modifica tablas ya existentes.

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS peliculas (
  id_pelicula      INT AUTO_INCREMENT PRIMARY KEY,
  id_externo       VARCHAR(30) NULL,
  nombre           VARCHAR(255) NOT NULL,
  sinopsis         TEXT NULL,
  poster_url       VARCHAR(500) NULL,
  duracion_min     INT NOT NULL,
  clasificacion    VARCHAR(20) NULL,
  cartelera_desde  DATE NULL,
  cartelera_hasta  DATE NULL,
  activo           BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE KEY uq_peliculas_id_externo (id_externo),
  CONSTRAINT chk_pelicula_duracion CHECK (duracion_min > 0),
  CONSTRAINT chk_pelicula_cartelera CHECK (
    cartelera_desde IS NULL OR cartelera_hasta IS NULL OR cartelera_hasta >= cartelera_desde
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS generos (
  id_genero  INT AUTO_INCREMENT PRIMARY KEY,
  nombre     VARCHAR(50) NOT NULL,
  UNIQUE KEY uq_generos_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pelicula_genero (
  id_pelicula  INT NOT NULL,
  id_genero    INT NOT NULL,
  PRIMARY KEY (id_pelicula, id_genero),
  CONSTRAINT fk_pg_pelicula FOREIGN KEY (id_pelicula) REFERENCES peliculas (id_pelicula),
  CONSTRAINT fk_pg_genero   FOREIGN KEY (id_genero)   REFERENCES generos (id_genero)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
