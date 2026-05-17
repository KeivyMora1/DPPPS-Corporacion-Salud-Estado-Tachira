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
    email         VARCHAR(100),
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
    descripcion TEXT,
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
    lugar               VARCHAR(150),
    descripcion         TEXT NOT NULL,
    participantes       INT NOT NULL DEFAULT 0,  -- Cantidad de personas beneficiadas
    eliminado           BOOLEAN NOT NULL DEFAULT FALSE, -- Soft delete
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Relaciones con otras tablas
    FOREIGN KEY (id_asic)             REFERENCES asic(id_asic),
    FOREIGN KEY (id_tipo)             REFERENCES tipo_actividad(id_tipo),
    FOREIGN KEY (id_usuario_registro) REFERENCES usuario(id_usuario)
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
-- TABLA: periodo
-- Representa un período de tiempo (mensual, trimestral, anual)
-- que el admin puede abrir o cerrar para consolidación.
-- ============================================================
CREATE TABLE IF NOT EXISTS periodo (
    id_periodo        INT AUTO_INCREMENT PRIMARY KEY,
    tipo              ENUM('mensual', 'trimestral', 'anual') NOT NULL,
    anio              INT NOT NULL,
    mes_inicio        INT,                       -- Mes donde empieza (1-12)
    mes_fin           INT,                       -- Mes donde termina (1-12)
    fecha_inicio      DATE NOT NULL,
    fecha_fin         DATE NOT NULL,
    estado            ENUM('abierto', 'cerrado') NOT NULL DEFAULT 'abierto',
    id_usuario_cierre INT,                       -- Admin que cerró el período
    fecha_cierre      DATETIME,
    motivo_reapertura TEXT,                      -- Si se reabrió, por qué
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario_cierre) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: informe_consolidado
-- Cabecera del informe generado. Agrupa las actividades
-- de un período determinado (y opcionalmente de un ASIC).
-- ============================================================
CREATE TABLE IF NOT EXISTS informe_consolidado (
    id_informe          INT AUTO_INCREMENT PRIMARY KEY,
    id_periodo          INT NOT NULL,
    id_asic             INT,                     -- NULL = informe general de todos los ASIC
    titulo              VARCHAR(200) NOT NULL,
    total_actividades   INT NOT NULL DEFAULT 0,
    total_participantes INT NOT NULL DEFAULT 0,
    observaciones       TEXT,
    id_usuario_generador INT NOT NULL,
    fecha_generacion    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_periodo)           REFERENCES periodo(id_periodo),
    FOREIGN KEY (id_asic)              REFERENCES asic(id_asic),
    FOREIGN KEY (id_usuario_generador) REFERENCES usuario(id_usuario)
);

-- ============================================================
-- TABLA: informe_detalle
-- Relaciona cada informe con las actividades que lo componen.
-- ============================================================
CREATE TABLE IF NOT EXISTS informe_detalle (
    id_detalle   INT AUTO_INCREMENT PRIMARY KEY,
    id_informe   INT NOT NULL,
    id_actividad INT NOT NULL,

    FOREIGN KEY (id_informe)   REFERENCES informe_consolidado(id_informe),
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad)
);

-- ============================================================
-- TABLA: importacion_log
-- Registro de cada vez que se importó un archivo Excel.
-- Guarda cuántas filas fueron exitosas y cuáles fallaron.
-- ============================================================
CREATE TABLE IF NOT EXISTS importacion_log (
    id_importacion  INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    nombre_archivo  VARCHAR(200) NOT NULL,
    total_filas     INT NOT NULL DEFAULT 0,
    filas_exitosas  INT NOT NULL DEFAULT 0,
    filas_error     INT NOT NULL DEFAULT 0,
    detalle_errores TEXT,                        -- JSON o texto con los errores por fila
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
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

-- Tipos de actividad de ejemplo
INSERT IGNORE INTO tipo_actividad (codigo, nombre, descripcion) VALUES
    ('TIPO-001', 'Jornada de Vacunación', 'Actividades de vacunación comunitaria'),
    ('TIPO-002', 'Consulta Médica', 'Consultas médicas generales y especializadas'),
    ('TIPO-003', 'Charla de Salud', 'Charlas y talleres de educación en salud'),
    ('TIPO-004', 'Jornada Odontológica', 'Atención odontológica a la comunidad'),
    ('TIPO-005', 'Actividad Deportiva', 'Actividades físicas y deportivas comunitarias');
