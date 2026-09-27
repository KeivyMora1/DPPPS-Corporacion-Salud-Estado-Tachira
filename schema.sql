-- ============================================================
-- db/schema.sql
-- Script completo para crear la base de datos del sistema DPPPS
-- Ejecutar este script una sola vez para inicializar la BD.
-- Compatible con MariaDB y MySQL.
-- ============================================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS dppps_informes
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE dppps_informes;

-- ============================================================
-- TABLA: usuario
-- Guarda los usuarios que pueden acceder al sistema.
-- Por ahora solo existe el rol "admin".
-- ============================================================
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario    INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,         -- La contraseña se guarda cifrada (bcrypt)
    nombre_completo VARCHAR(100) NOT NULL,
    nombre        VARCHAR(100) NULL,
    apellido      VARCHAR(100) NULL,
    email         VARCHAR(100),
    email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    codigo_verificacion VARCHAR(20) NULL,
    codigo_verificacion_expira DATETIME NULL,
    codigo_recuperacion VARCHAR(20) NULL,
    codigo_recuperacion_expira DATETIME NULL,
    activo        BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE = usuario desactivado
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: asic
-- Catálogo de Áreas de Salud Integral Comunitaria.
-- No guarda actividades, solo los nombres de las áreas.
-- ============================================================
CREATE TABLE IF NOT EXISTS asic (
    id_asic    INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,      -- Ej: "ASIC-001"
    nombre     VARCHAR(100) NOT NULL,
    municipio  VARCHAR(100),
    parroquia  VARCHAR(100),
    activo     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: tipo_actividad
-- Catálogo de tipos de actividad (ej: Jornada de vacunación,
-- Consulta médica, Charla de salud, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS tipo_actividad (
    id_tipo    INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,      -- Ej: "TIPO-001"
    nombre     VARCHAR(100) NOT NULL,
    activo     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: actividad
-- Registro principal. Aquí se guarda cada actividad realizada
-- por un ASIC. Es el corazón del sistema.
-- ============================================================
CREATE TABLE IF NOT EXISTS actividad (
    id_actividad        INT AUTO_INCREMENT PRIMARY KEY,
    id_asic             INT NOT NULL,
    id_tipo             INT NOT NULL,
    id_usuario_registro INT NOT NULL,            -- Quién registró esta actividad
    fecha_inicio        DATE NOT NULL,
    fecha_fin           DATE NOT NULL,
    -- Ubicación detallada (campos de la plantilla de importación)
    estado              VARCHAR(100),
    municipio           VARCHAR(100),
    parroquia           VARCHAR(100),
    establecimiento_salud VARCHAR(100),
    nombre_establecimiento VARCHAR(150),
    comites_salud       VARCHAR(150),
    descripcion         TEXT NOT NULL,           -- TEMA TRATADO
    -- Participantes por categoría (plantilla de importación)
    medicos             INT NOT NULL DEFAULT 0,
    promotores_salud    INT NOT NULL DEFAULT 0,
    voceros_comite_salud INT NOT NULL DEFAULT 0,
    vocero_consejo_direccion INT NOT NULL DEFAULT 0,
    coordinador_docencia INT NOT NULL DEFAULT 0,
    autoridades_presentes INT NOT NULL DEFAULT 0,
    otros_actores       INT NOT NULL DEFAULT 0,
    personas_comunidad  INT NOT NULL DEFAULT 0,
    estudiantes_aspirantes INT NOT NULL DEFAULT 0,
    participantes       INT NOT NULL DEFAULT 0,  -- TOTAL DE ASISTENCIA (suma o campo directo)
    eliminado           BOOLEAN NOT NULL DEFAULT FALSE, -- Soft delete
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Relaciones con otras tablas
    FOREIGN KEY (id_asic)             REFERENCES asic(id_asic),
    FOREIGN KEY (id_tipo)             REFERENCES tipo_actividad(id_tipo),
    FOREIGN KEY (id_usuario_registro) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: tipo_voceria
-- Catálogo de tipos de vocería (ej: Reunión, Asamblea, Jornada)
-- ============================================================
CREATE TABLE IF NOT EXISTS tipo_voceria (
    id_tipo    INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,      -- Ej: "VOC-001"
    nombre     VARCHAR(100) NOT NULL,
    activo     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: voceria
-- Cabecera de cada registro de vocería CS
-- ============================================================
CREATE TABLE IF NOT EXISTS voceria (
    id_voceria           INT AUTO_INCREMENT PRIMARY KEY,
    id_asic              INT NOT NULL,
    id_tipo              INT NOT NULL,           -- Tipo general (ej: Vocería CS)
    id_usuario_registro  INT NOT NULL,
    estado               VARCHAR(100),
    municipio            VARCHAR(100),
    parroquia            VARCHAR(100),
    centro_dispensador   VARCHAR(100),           -- Centro dispensador general para toda la vocería
    nombre_centro        VARCHAR(150),          -- Nombre del centro general para toda la vocería
    nombre_comite        VARCHAR(150),          -- Nombre del comité general para toda la vocería
    eliminado            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (id_asic)             REFERENCES asic(id_asic),
    FOREIGN KEY (id_tipo)             REFERENCES tipo_voceria(id_tipo),
    FOREIGN KEY (id_usuario_registro) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: voceria_item
-- Detalle de cada vocero/participante dentro de una sesión de vocería
-- ============================================================
CREATE TABLE IF NOT EXISTS voceria_item (
    id_item           INT AUTO_INCREMENT PRIMARY KEY,
    id_voceria        INT NOT NULL,
    id_tipo_voceria   INT NOT NULL,           -- Tipo específico de vocería (ej: V. CONTRALORÍA, V. SALUD Y VIDA, etc.)
    nombres           VARCHAR(150) NOT NULL,
    ci                VARCHAR(20) NOT NULL,
    telefono          VARCHAR(30),
    fecha_nacimiento  DATE,
    edad              INT,
    sexo              ENUM('M', 'F'),
    profesion         VARCHAR(100),
    correo            VARCHAR(100),
    fechas_eleccion   DATE,
    eliminado         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (id_voceria)      REFERENCES voceria(id_voceria),
    FOREIGN KEY (id_tipo_voceria) REFERENCES tipo_voceria(id_tipo)
);

-- ============================================================
-- TABLA: evidencia
-- Archivos o fotos que se adjuntan a una actividad como prueba.
-- ============================================================
CREATE TABLE IF NOT EXISTS evidencia (
    id_evidencia   INT AUTO_INCREMENT PRIMARY KEY,
    id_actividad   INT NOT NULL,
    nombre_archivo VARCHAR(200) NOT NULL,        -- Nombre original del archivo
    ruta_archivo   VARCHAR(500) NOT NULL,        -- Ruta donde está guardado en el servidor
    tipo_archivo   VARCHAR(50),                  -- Ej: "image/jpeg", "application/pdf"
    tamano_bytes   INT,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad)
);

-- ============================================================
-- DATOS INICIALES (Seed)
-- Se inserta el usuario administrador por defecto.
-- Contraseña: "admin123" cifrada con bcrypt
-- (El hash se genera con Python, este es un ejemplo)
-- ============================================================

-- Usuario admin por defecto
INSERT IGNORE INTO usuario (username, password_hash, nombre_completo, email)
VALUES (
    'admin',
    '$2b$12$PLACEHOLDER_HASH',   -- Este hash se reemplaza al ejecutar el setup inicial
    'Administrador del Sistema',
    'admin@dppps.gob.ve'
);

-- Tipos de actividad permitidos por la plantilla de importación
INSERT IGNORE INTO tipo_actividad (codigo, nombre) VALUES
    ('TIPO-01', 'Salud toca tu puerta'),
    ('TIPO-02', 'Sesiones educativas'),
    ('TIPO-03', 'Los Comités de Salud van a la escuela'),
    ('TIPO-04', 'Actividades de Promoción y Prevención Social'),
    ('TIPO-05', 'Participación Activa en Jornadas'),
    ('TIPO-06', 'Participación Activa en Inmunizaciones'),
    ('TIPO-07', 'Entrevista servicio social');

-- Tipos de vocería permitidos
INSERT IGNORE INTO tipo_voceria (codigo, nombre) VALUES
    ('VOC-01', 'V. CONTRALORÍA'),
    ('VOC-02', 'V. DEL ADULTO MAYOR'),
    ('VOC-03', 'V. DE ENFERMEDADES CRÓNICAS TRASMISIBLES Y NO TRASMISIBLES'),
    ('VOC-04', 'V. DE PERSONAS CON DISCAPACIDAD, ENCAMADOS Y CUIDADORES EN SALUD'),
    ('VOC-05', 'V. DE SALUD Y VIDA'),
    ('VOC-06', 'V. DE NIÑOS, NIÑAS Y ADOLESCENTES'),
    ('VOC-07', 'V. DE LA JUVENTUD EN SALUD'),
    ('VOC-08', 'V. DE EDUCACIÓN POPULAR EN SALUD INTERCULTURAL Y ANCESTRAL'),
    ('VOC-09', 'V. DE INMUNIZACIONES'),
    ('VOC-10', 'V. DE PROYECTOS EN SALUD');
