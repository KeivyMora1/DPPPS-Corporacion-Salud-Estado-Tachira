-- ============================================================
-- db/schema.sql
-- Script completo para crear la base de datos del sistema DPPPS
-- Ejecutado por python -m db.setup para inicializar la BD desde cero.
-- Compatible con MariaDB y MySQL.
-- ============================================================

CREATE DATABASE IF NOT EXISTS dppps_informes
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE dppps_informes;

-- ============================================================
-- TABLA: usuario
-- ============================================================
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    nombre VARCHAR(100) NULL,
    apellido VARCHAR(100) NULL,
    email VARCHAR(120) NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'lector',
    email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    codigo_verificacion VARCHAR(20) NULL,
    codigo_verificacion_expira DATETIME NULL,
    codigo_recuperacion VARCHAR(20) NULL,
    codigo_recuperacion_expira DATETIME NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: asic
-- Modelo nuevo solicitado:
-- id, nombre, created_at
-- Mantenemos compatibilidad con el sistema actual.
-- ============================================================
CREATE TABLE IF NOT EXISTS asic (
    id_asic INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_asic_nombre (nombre)
);

-- ============================================================
-- TABLA: municipio
-- ============================================================
CREATE TABLE IF NOT EXISTS municipio (
    id_municipio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_municipio_nombre (nombre)
);

-- ============================================================
-- TABLA: parroquia
-- ============================================================
CREATE TABLE IF NOT EXISTS parroquia (
    id_parroquia INT AUTO_INCREMENT PRIMARY KEY,
    id_municipio INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_parroquia_municipio_nombre (id_municipio, nombre),
    FOREIGN KEY (id_municipio) REFERENCES municipio(id_municipio) ON DELETE RESTRICT
);

-- ============================================================
-- TABLA: tipo_actividad
-- Modelo solicitado:
-- id, nombre, created_at
-- Mantenemos compatibilidad con el sistema actual.
-- ============================================================
CREATE TABLE IF NOT EXISTS tipo_actividad (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_tipo_actividad_nombre (nombre)
);

-- ============================================================
-- TABLA: actividad
-- Modelo solicitado con una sola fecha.
-- ============================================================
CREATE TABLE IF NOT EXISTS actividad (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_asic INT NOT NULL,
    id_tipo INT NOT NULL,
    id_usuario_registro INT NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR(100) NULL,
    municipio VARCHAR(100) NULL,
    parroquia VARCHAR(100) NULL,
    establecimiento_salud VARCHAR(150) NULL,
    nombre_establecimiento VARCHAR(200) NULL,
    comites_salud INT NULL,
    tema TEXT NOT NULL,
    cant_medicos INT NOT NULL DEFAULT 0,
    cant_promotores_salud INT NOT NULL DEFAULT 0,
    cant_voceros_comite_salud INT NOT NULL DEFAULT 0,
    cant_vocero_consejo_direccion INT NOT NULL DEFAULT 0,
    cant_coordinador_docencia INT NOT NULL DEFAULT 0,
    cant_autoridades INT NOT NULL DEFAULT 0,
    cant_otros_actores INT NOT NULL DEFAULT 0,
    cant_personas_comunidad INT NOT NULL DEFAULT 0,
    cant_estudiantes_aspirantes INT NOT NULL DEFAULT 0,
    total_participantes INT NOT NULL DEFAULT 0,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_asic) REFERENCES asic(id_asic),
    FOREIGN KEY (id_tipo) REFERENCES tipo_actividad(id_tipo),
    FOREIGN KEY (id_usuario_registro) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: tipo_voceria
-- Modelo solicitado sin codigo ni activo.
-- ============================================================
CREATE TABLE IF NOT EXISTS tipo_voceria (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_tipo_voceria_nombre (nombre)
);

-- ============================================================
-- TABLA: comite
-- Renombramiento de la cabecera actual de vocería.
-- ============================================================
CREATE TABLE IF NOT EXISTS comite (
    id_comite INT AUTO_INCREMENT PRIMARY KEY,
    id_asic INT NOT NULL,
    id_usuario_registro INT NOT NULL,
    estado VARCHAR(100) NULL,
    municipio VARCHAR(100) NULL,
    parroquia VARCHAR(100) NULL,
    centro_dispensador VARCHAR(100) NULL,
    nombre_centro VARCHAR(200) NULL,
    nombre_comite VARCHAR(200) NULL,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_asic) REFERENCES asic(id_asic),
    FOREIGN KEY (id_usuario_registro) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: voceria
-- Modelo solicitado: registro del representante / vocero.
-- Se mantiene la estructura actual del detalle de vocería para
-- compatibilidad con la lógica actual del sistema.
-- ============================================================
CREATE TABLE IF NOT EXISTS voceria (
    id_voceria INT AUTO_INCREMENT PRIMARY KEY,
    id_comite INT NOT NULL,
    id_tipo_voceria INT NOT NULL,
    nombres VARCHAR(150) NOT NULL,
    ci VARCHAR(30) NOT NULL,
    telefono VARCHAR(30) NULL,
    fecha_nacimiento DATE NULL,
    edad INT NULL,
    sexo ENUM('M', 'F') NULL,
    profesion VARCHAR(120) NULL,
    correo VARCHAR(120) NULL,
    fechas_eleccion DATE NULL,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_comite) REFERENCES comite(id_comite),
    FOREIGN KEY (id_tipo_voceria) REFERENCES tipo_voceria(id_tipo)
);

-- ============================================================
-- SEEDS
-- ============================================================
INSERT IGNORE INTO asic (nombre) VALUES
    ('Andrés Bello'),
    ('Antonio Rómulo Costa'),
    ('Ayacucho'),
    ('Bolívar'),
    ('Capacho Libertad'),
    ('Cárdenas'),
    ('Córdoba'),
    ('Dr. Hugo Murzi'),
    ('Dr. Jacinto Convit'),
    ('Dr. José María Vargas'),
    ('Fernández Feo'),
    ('García de Hevia'),
    ('Guásimos'),
    ('Independencia'),
    ('Jáuregui'),
    ('Junin · Rafael Urdaneta'),
    ('Libertador'),
    ('Michelena'),
    ('Panamericano · San Judas Tadeo'),
    ('Sabaneta'),
    ('Samuel Darío Maldonado'),
    ('San Josecito'),
    ('Sucre'),
    ('Ureña'),
    ('Uribante');

INSERT IGNORE INTO tipo_actividad (nombre) VALUES
    ('Salud toca tu puerta'),
    ('Sesiones educativas'),
    ('Los Comités de Salud van a la escuela'),
    ('Actividades de Promoción y Prevención Social'),
    ('Participación Activa en Jornadas'),
    ('Participación Activa en Inmunizaciones'),
    ('Entrevista servicio social');

INSERT IGNORE INTO tipo_voceria (nombre) VALUES
    ('V. CONTRALORÍA'),
    ('V. DEL ADULTO MAYOR'),
    ('V. DE ENFERMEDADES CRÓNICAS TRASMISIBLES Y NO TRASMISIBLES'),
    ('V. DE PERSONAS CON DISCAPACIDAD, ENCAMADOS Y CUIDADORES EN SALUD'),
    ('V. DE SALUD Y VIDA'),
    ('V. DE NIÑOS, NIÑAS Y ADOLESCENTES'),
    ('V. DE LA JUVENTUD EN SALUD'),
    ('V. DE EDUCACIÓN POPULAR EN SALUD INTERCULTURAL Y ANCESTRAL'),
    ('V. DE INMUNIZACIONES'),
    ('V. DE PROYECTOS EN SALUD');

INSERT IGNORE INTO municipio (id_municipio, nombre) VALUES
    (1, 'Andrés Bello'),
    (2, 'Antonio Rómulo Costa'),
    (3, 'Ayacucho'),
    (4, 'Bolívar'),
    (5, 'Cárdenas'),
    (6, 'Córdoba'),
    (7, 'Fernández Feo'),
    (8, 'Francisco de Miranda'),
    (9, 'García de Hevia'),
    (10, 'Guásimos'),
    (11, 'Independencia'),
    (12, 'Jáuregui'),
    (13, 'José María Vargas'),
    (14, 'Junín'),
    (15, 'Libertad'),
    (16, 'Libertador'),
    (17, 'Lobatera'),
    (18, 'Michelena'),
    (19, 'Panamericano'),
    (20, 'Pedro María Ureña'),
    (21, 'Rafael Urdaneta'),
    (22, 'Samuel Darío Maldonado'),
    (23, 'San Cristóbal'),
    (24, 'San Judas Tadeo'),
    (25, 'Seboruco'),
    (26, 'Simón Rodríguez'),
    (27, 'Sucre'),
    (28, 'Torbes'),
    (29, 'Uribante');

INSERT IGNORE INTO parroquia (id_municipio, nombre) VALUES
    (1, 'Cordero'),
    (2, 'Virgen del Carmen'),
    (3, 'San Juan de Colón'),
    (3, 'Rivas Berti'),
    (3, 'San Pedro del Río'),
    (4, 'San Antonio del Táchira'),
    (4, 'Palotal'),
    (4, 'Juan Vicente Gómez'),
    (4, 'Isaías Medina Angarita'),
    (5, 'Táriba'),
    (5, 'Amenodoro Rangel Lamús'),
    (5, 'La Florida'),
    (6, 'Santa Ana del Táchira'),
    (7, 'San Rafael del Piñal'),
    (7, 'Alberto Adriani'),
    (7, 'Santo Domingo'),
    (8, 'San José de Bolívar'),
    (9, 'La Fría'),
    (9, 'Boca de Grita'),
    (9, 'José Antonio Páez'),
    (10, 'Palmira'),
    (11, 'Capacho Nuevo'),
    (11, 'Juan Germán Roscio'),
    (11, 'Román Cárdenas'),
    (12, 'La Grita'),
    (12, 'Emilio Constantino Guerrero'),
    (12, 'Monseñor Miguel Antonio Salas'),
    (13, 'El Cobre'),
    (14, 'Rubio'),
    (14, 'Bramón'),
    (14, 'La Petrólea'),
    (14, 'Quinimarí'),
    (15, 'Capacho Viejo'),
    (15, 'Cipriano Castro'),
    (15, 'Manuel Felipe Rugeles'),
    (16, 'Abejales'),
    (16, 'Doradas'),
    (16, 'Emeterio Ochoa'),
    (16, 'San Joaquín de Navay'),
    (17, 'Lobatera'),
    (17, 'Constitución'),
    (18, 'Michelena'),
    (19, 'San Pablo'),
    (19, 'La Palmita'),
    (20, 'Ureña'),
    (20, 'Nueva Arcadia'),
    (21, 'Delicias'),
    (22, 'La Tendida'),
    (22, 'Boconó'),
    (22, 'Hernández'),
    (23, 'La Concordia'),
    (23, 'Pedro María Morantes'),
    (23, 'San Juan Bautista'),
    (23, 'San Sebastián'),
    (23, 'Francisco Romero Lobo'),
    (24, 'San Judas Tadeo'),
    (25, 'Seboruco'),
    (26, 'San Simón'),
    (27, 'Sucre'),
    (27, 'Eleazar López Contreras'),
    (27, 'San Pablo'),
    (28, 'San Josecito'),
    (29, 'Pregonero'),
    (29, 'Cárdenas'),
    (29, 'Juan Pablo Peñaloza'),
    (29, 'Potosí');
