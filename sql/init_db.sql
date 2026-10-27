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
	numero_sala INT NOT NULL UNIQUE,
	capacidad INT NOT NULL,
	activa BOOLEAN NOT NULL DEFAULT TRUE,
	FOREIGN KEY(id_local) REFERENCES locales(id_local),
	CONSTRAINT uq_salas_local_numero UNIQUE (id_local, numero_sala),
    CONSTRAINT chk_salas_numero CHECK (numero_sala > 0)
	CONSTRAINT chk_salas_capacidad CHECK (capacidad > 0)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS butacas (
	id_butaca INT AUTO_INCREMENT PRIMARY KEY,
	id_sala INT NOT NULL,
	fila CHAR(1) NOT NULL,
	numero INT NOT NULL,
	activa BOOLEAN NOT NULL DEFAULT TRUE,
	FOREIGN KEY (id_sala) REFERENCES salas(id_sala),
    CONSTRAINT uq_butacas_asiento UNIQUE (id_sala, fila, numero),
    CONSTRAINT chk_butacas_numero CHECK (numero > 0)
);
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'administrador') NOT NULL DEFAULT 'cliente',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



