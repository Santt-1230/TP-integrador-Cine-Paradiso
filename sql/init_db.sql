SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cine_paradiso
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;

USE cine_paradiso;

CREATE TABLE IF NOT EXISTS locales(
	id_local INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL UNIQUE,
	direccion VARCHAR(200) NOT NULL UNIQUE,
	activo  BOOLEAN NOT NULL DEFAULT TRUE)
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS salas(
	id_sala INT AUTO_INCREMENT PRIMARY KEY,
	id_local INT NOT NULL,
	numero_sala INT NOT NULL NULL,
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
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
	apellido VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
	fecha_nacimiento DATE NOT NULL,
    rol ENUM('cliente', 'administrador') NOT NULL DEFAULT 'cliente',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
INSERT INTO usuarios (nombre, apellido, email, fecha_nacimiento, contrasena_hash, rol) VALUES ('Admnin', 'Cine Paradiso', 'admin@cineparadiso.com', '1990-01-01', 
'scrypt:32768:8:1$XogwXYeb1jrrnFYg$44a1bc2bc965551d7375ccb96e0b662cc87cf91ce52cfa37b3a547b99ca8e59b60ec7ba5243baa8a7dc199e36064d06ed0d4ccf83cb46af5cefc4e12c24fd819', 'administrador'); 



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
	Foreign Key (id_funcion) REFERENCES funciones(id_usuario)
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

CREATE TABLE IF NOT EXISTS compra_productos (
	id_compra_producto INT AUTO_INCREMENT PRIMARY KEY,
	id_compra INT NOT NULL,
	id_producto INT NOT NULL,
	cantidad INT NOT NULL DEFAULT 1 CHECK (cantidad > 0),
	precio_unitario DECIMAL(10,2) NOT NULL,
	FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
	FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

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


