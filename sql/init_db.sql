SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cine_paradiso
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;

USE cine_paradiso;

CREATE TABLE IF NOT EXISTS locales(
	id_local INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL UNIQUE,
	direccion VARCHAR(200) NOT NULL UNIQUE,
	activo BOOLEAN NOT NULL DEFAULT TRUE
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS salas(
	id_sala INT AUTO_INCREMENT PRIMARY KEY,
	id_local INT NOT NULL,
	numero_sala INT NOT NULL,
	capacidad INT NOT NULL,
	estado ENUM('activa', 'inactiva') NOT NULL DEFAULT 'activa',
	FOREIGN KEY(id_local) REFERENCES locales(id_local),
	CONSTRAINT uq_salas_local_numero UNIQUE (id_local, numero_sala),
    CONSTRAINT chk_salas_numero CHECK (numero_sala > 0),
	CONSTRAINT chk_salas_capacidad CHECK (capacidad > 0)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS butacas (
	id_butaca INT AUTO_INCREMENT PRIMARY KEY,
	id_sala INT NOT NULL,
	fila CHAR(1) NOT NULL,
	numero INT NOT NULL,
	FOREIGN KEY (id_sala) REFERENCES salas(id_sala),
    CONSTRAINT uq_butacas_asiento UNIQUE (id_sala, fila, numero),
    CONSTRAINT chk_butacas_numero CHECK (numero > 0)
);
-- Peliculas y cartelera
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

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
	apellido VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
	fecha_nacimiento DATE NOT NULL,
    rol ENUM('cliente', 'administrador') NOT NULL DEFAULT 'cliente',
    activo BOOLEAN NOT NULL DEFAULT TRUE

)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS peliculas (
	id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
	id_externo VARCHAR(30) NULL UNIQUE,
	nombre VARCHAR(255) NOT NULL,
	sinopsis TEXT,
	poster_url VARCHAR(500),
	duracion_min INT NOT NULL,
	clasificacion VARCHAR(20),
	cartelera_desde DATE,
	cartelera_hasta DATE,
	activo BOOLEAN NOT NULL DEFAULT TRUE,
	CONSTRAINT chk_peliculas_duracion CHECK (duracion_min > 0)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



CREATE TABLE IF NOT EXISTS funciones (
	id_funcion INT AUTO_INCREMENT PRIMARY KEY,
	id_pelicula INT NOT NULL,
	id_sala INT NOT NULL,
	fecha_hora_inicio DATETIME NOT NULL,
	fecha_hora_fin DATETIME NOT NULL,
	precio_entrada DECIMAL(10,2) NOT NULL,
	estado ENUM('programada', 'cancelada', 'finalizada') NOT NULL DEFAULT 'programada',
	FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula),
	FOREIGN KEY (id_sala) REFERENCES salas(id_sala),
	CONSTRAINT chk_funciones_fechas CHECK (fecha_hora_fin > fecha_hora_inicio),
	CONSTRAINT chk_funciones_precio CHECK (precio_entrada >= 0)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

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


CREATE TABLE IF NOT EXISTS compras (
	id_compra INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	id_funcion INT NOT NULL,
	estado ENUM('pendiente', 'confirmada', 'cancelada', 'expirada') NOT NULL DEFAULT 'pendiente',
	fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	expira_en DATETIME NOT NULL,
	fecha_confirmacion DATETIME NOT NULL,
	total DECIMAL(10,2) NOT NULL DEFAULT 0,
	numero_factura VARCHAR(30) NULL UNIQUE,
	fecha_cancelacion DATETIME NULL,
	motivo_cancelacion ENUM('cliente', ' funcion_cancelada') NULL,
	monto_reembolsado DECIMAL(10,2) NULL,
	Foreign Key (id_usuario) REFERENCES usuarios(id_usuario),
	Foreign Key (id_funcion) REFERENCES funciones(id_funcion)
);

CREATE TABLE IF NOT EXISTS entradas(
	id_entrada INT AUTO_INCREMENT PRIMARY KEY,
	id_compra INT NOT NULL,
	id_funcion INT NOT NULL,
	id_butaca INT NOT NULL,
	precio_unitario DECIMAL(10,2) NOT NULL,
	estado ENUM('reservada', 'confirmada', 'utilizada', 'cancelada') NOT NULL DEFAULT 'reservada',
	token_qr VARCHAR(255) NULL UNIQUE,
    fecha_uso DATETIME NULL,
	butaca_ocupada INT GENERATED ALWAYS AS (CASE WHEN estado = 'cancelada' THEN NULL ELSE id_butaca END) STORED,
	Foreign Key (id_compra) REFERENCES compras(id_compra),
	Foreign Key (id_funcion) REFERENCES funciones(id_funcion),
	Foreign Key (id_butaca) REFERENCES butacas(id_butaca),
);
CREATE TABLE IF NOT EXISTS productos (
	id_producto INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	tipo ENUM('comida', 'bebida', 'estacionamiento', 'vip') NOT NULL,
	descripcion VARCHAR(255),
	precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
	activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS promociones (
	id_promocion INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(150) NOT NULL,
	descripcion VARCHAR(300),
	imagen_url VARCHAR(500),
	vigente_desde DATE NOT NULL,
	vigente_hasta DATE NOT NULL,
	activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS compras (
	id_compra INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	id_funcion INT NOT NULL,
	estado ENUM('pendiente', 'confirmada', 'cancelada', 'expirada') NOT NULL DEFAULT 'pendiente',
	fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	expira_en DATETIME NOT NULL,
	fecha_confirmacion DATETIME NOT NULL,
	total DECIMAL(10,2) NOT NULL DEFAULT 0,
	numero_factura VARCHAR(30) NULL UNIQUE,
	fecha_cancelacion DATETIME NULL,
	motivo_cancelacion ENUM('cliente', ' funcion_cancelada') NULL,
	monto_reembolsado DECIMAL(10,2) NULL,
	Foreign Key (id_usuario) REFERENCES usuarios(id_usuario),
	Foreign Key (id_funcion) REFERENCES funciones(id_funcion)
);

CREATE TABLE IF NOT EXISTS compra_productos (
	id_compra_producto INT AUTO_INCREMENT PRIMARY KEY,
	id_compra INT NOT NULL,
	id_producto INT NOT NULL,
	fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	cantidad INT NOT NULL DEFAULT 1 CHECK (cantidad > 0),
	precio_unitario DECIMAL(10,2) NOT NULL,
	FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
	FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);


INSERT INTO usuarios (nombre, apellido, email, fecha_nacimiento, contrasena_hash, rol) VALUES (
	'Admin', 'Cine Paradiso', 'admin@cineparadiso.com', '1990-01-01', 
'scrypt:32768:8:1$XogwXYeb1jrrnFYg$44a1bc2bc965551d7375ccb96e0b662cc87cf91ce52cfa37b3a547b99ca8e59b60ec7ba5243baa8a7dc199e36064d06ed0d4ccf83cb46af5cefc4e12c24fd819', 'administrador'); 



INSERT INTO locales (nombre, direccion) VALUES
    ('Paradiso Centro', 'Calle Falsa 123'),
    ('Paradiso Norte', 'Avenida Ejemplo 456'),
    ('Paradiso Sur', 'Calle de Prueba 789');
INSERT INTO salas (id_local, numero_sala, capacidad) VALUES
    (1, 1, 6),
    (2, 1, 6);

INSERT INTO butacas (id_sala, fila, numero) VALUES
    (1, 'A', 1), (1, 'A', 2), (1, 'A', 3),
    (1, 'B', 1), (1, 'B', 2), (1, 'B', 3),
    (2, 'A', 1), (2, 'A', 2), (2, 'A', 3),
    (2, 'B', 1), (2, 'B', 2), (2, 'B', 3);




-- Datos de ejemplo: peliculas, generos y relaciones

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

/*!40000 ALTER TABLE `generos` DISABLE KEYS */;
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (1,'Acción');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (6,'Aventura');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (2,'Ciencia ficción');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (13,'Comedia');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (5,'Crimen');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (7,'Drama');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (10,'Suspense');
/*!40000 ALTER TABLE `generos` ENABLE KEYS */;

/*!40000 ALTER TABLE `peliculas` DISABLE KEYS */;
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (1,'603','Matrix','Thomas Anderson lleva una doble vida: por el día es programador en una importante empresa de software, y por la noche un hacker informático llamado Neo. Su vida no volverá a ser igual cuando unos misteriosos personajes le inviten a descubrir la respuesta a la pregunta que no le deja dormir: ¿qué es Matrix?','https://image.tmdb.org/t/p/w500/tpW2X2DvxtTHJ61iJ7zNYYrJihs.jpg',138,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (2,'27205','Origen','Dom Cobb es un ladrón hábil, el mejor de todos, especializado en el peligroso arte de extracción: el robo de secretos valiosos desde las profundidades del subconsciente durante el estado de sueño cuando la mente está más vulnerable. Esta habilidad excepcional de Cobb le ha hecho un jugador codiciado en el traicionero nuevo mundo de espionaje corporativo, pero al mismo tiempo, le ha convertido en un fugitivo internacional y ha tenido que sacrificar todo que le importaba. Ahora a Cobb se le ofrece una oportunidad para redimirse. Con un último trabajo podría recuperar su vida anterior, pero solamente si logra lo imposible.','https://image.tmdb.org/t/p/w500/tXQvtRWfkUUnWJAn2tN3jERIUG.jpg',148,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (3,'157336','Interstellar','Un grupo de exploradores hacen uso de un agujero de gusano recientemente descubierto para superar las limitaciones de los viajes espaciales tripulados y vencer las inmensas distancias que tiene un viaje interestelar.','https://image.tmdb.org/t/p/w500/d1QKiYtceF3GDtxvTFXFAqwwah9.jpg',169,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (4,'550','El club de la lucha','Un hombre consumido por el insomnio y una vida sin sentido conoce a Tyler Durden, un carismático anarquista que lo arrastra a un club secreto donde el dolor despierta algo dormido. Lo que comienza como liberación pronto se convierte en una guerra contra el sistema…','https://image.tmdb.org/t/p/w500/sgTAWJFaB2kBvdQxRGabYFiQqEK.jpg',139,'+18','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (5,'680','Pulp Fiction','Jules y Vincent, dos asesinos a sueldo con muy pocas luces, trabajan para Marsellus Wallace. Vincent le confiesa a Jules que Marsellus le ha pedido que cuide de Mia, su mujer. Jules le recomienda prudencia porque es muy peligroso sobrepasarse con la novia del jefe. Cuando llega la hora de trabajar, ambos deben ponerse manos a la obra. Su misión: recuperar un misterioso maletín.','https://image.tmdb.org/t/p/w500/hNcQAuquJxTxl2fJFs1R42DrWcf.jpg',154,'+18','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (6,'155','El caballero oscuro','Batman/Bruce Wayne regresa para continuar su guerra contra el crimen. Con la ayuda del teniente Jim Gordon y del Fiscal del Distrito Harvey Dent, Batman se propone destruir el crimen organizado en la ciudad de Gotham. El triunvirato demuestra su eficacia, pero, de repente, aparece Joker, un nuevo criminal que desencadena el caos y tiene aterrados a los ciudadanos.','https://image.tmdb.org/t/p/w500/8QDQExnfNFOtabLDKqfDQuHDsIg.jpg',152,'+13','2026-10-31','2027-12-31',1);
/*!40000 ALTER TABLE `peliculas` ENABLE KEYS */;

/*!40000 ALTER TABLE `pelicula_genero` DISABLE KEYS */;
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (1,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (1,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,6);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,7);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (4,7);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (4,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,13);
/*!40000 ALTER TABLE `pelicula_genero` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

