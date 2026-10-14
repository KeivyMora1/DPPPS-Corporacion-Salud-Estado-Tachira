-- MySQL dump 10.13  Distrib 26.7.0, for Win64 (x86_64)
--
-- Host: localhost    Database: dppps_informes
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

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

--
-- Table structure for table `actividad`
--

DROP TABLE IF EXISTS `actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividad` (
  `id_actividad` int(11) NOT NULL AUTO_INCREMENT,
  `id_asic` int(11) NOT NULL,
  `id_tipo` int(11) NOT NULL,
  `id_usuario_registro` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(100) DEFAULT NULL,
  `municipio` varchar(100) DEFAULT NULL,
  `parroquia` varchar(100) DEFAULT NULL,
  `establecimiento_salud` varchar(150) DEFAULT NULL,
  `nombre_establecimiento` varchar(200) DEFAULT NULL,
  `comites_salud` int(11) DEFAULT NULL,
  `tema` text NOT NULL,
  `cant_medicos` int(11) NOT NULL DEFAULT 0,
  `cant_promotores_salud` int(11) NOT NULL DEFAULT 0,
  `cant_voceros_comite_salud` int(11) NOT NULL DEFAULT 0,
  `cant_vocero_consejo_direccion` int(11) NOT NULL DEFAULT 0,
  `cant_coordinador_docencia` int(11) NOT NULL DEFAULT 0,
  `cant_autoridades` int(11) NOT NULL DEFAULT 0,
  `cant_otros_actores` int(11) NOT NULL DEFAULT 0,
  `cant_personas_comunidad` int(11) NOT NULL DEFAULT 0,
  `cant_estudiantes_aspirantes` int(11) NOT NULL DEFAULT 0,
  `total_participantes` int(11) NOT NULL DEFAULT 0,
  `eliminado` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_actividad`),
  KEY `id_asic` (`id_asic`),
  KEY `id_tipo` (`id_tipo`),
  KEY `id_usuario_registro` (`id_usuario_registro`),
  CONSTRAINT `actividad_ibfk_1` FOREIGN KEY (`id_asic`) REFERENCES `asic` (`id_asic`),
  CONSTRAINT `actividad_ibfk_2` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_actividad` (`id_tipo`),
  CONSTRAINT `actividad_ibfk_3` FOREIGN KEY (`id_usuario_registro`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actividad`
--

LOCK TABLES `actividad` WRITE;
/*!40000 ALTER TABLE `actividad` DISABLE KEYS */;
INSERT INTO `actividad` VALUES (7,1,4,2,'2026-10-14','Táchira','Junín','Quinimarí','CDI','sadfasdfasd',0,'asdfsadfsad',5,4,5,4,5,1,2,45,4,75,0,'2026-10-14 11:33:51','2026-10-14 11:33:51');
/*!40000 ALTER TABLE `actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asic`
--

DROP TABLE IF EXISTS `asic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asic` (
  `id_asic` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_asic`),
  UNIQUE KEY `ux_asic_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asic`
--

LOCK TABLES `asic` WRITE;
/*!40000 ALTER TABLE `asic` DISABLE KEYS */;
INSERT INTO `asic` VALUES (1,'Andrés Bello','2026-10-13 16:52:34','2026-10-13 16:52:34'),(2,'Antonio Rómulo Costa','2026-10-13 16:52:34','2026-10-13 16:52:34'),(3,'Ayacucho','2026-10-13 16:52:34','2026-10-13 16:52:34'),(4,'Bolívar','2026-10-13 16:52:34','2026-10-13 16:52:34'),(5,'Capacho Libertad','2026-10-13 16:52:34','2026-10-13 16:52:34'),(6,'Cárdenas','2026-10-13 16:52:34','2026-10-13 16:52:34'),(7,'Córdoba','2026-10-13 16:52:34','2026-10-13 16:52:34'),(8,'Dr. Hugo Murzi','2026-10-13 16:52:34','2026-10-13 16:52:34'),(9,'Dr. Jacinto Convit','2026-10-13 16:52:34','2026-10-13 16:52:34'),(10,'Dr. José María Vargas','2026-10-13 16:52:34','2026-10-13 16:52:34'),(11,'Fernández Feo','2026-10-13 16:52:34','2026-10-13 16:52:34'),(12,'García de Hevia','2026-10-13 16:52:34','2026-10-13 16:52:34'),(13,'Guásimos','2026-10-13 16:52:34','2026-10-13 16:52:34'),(14,'Independencia','2026-10-13 16:52:34','2026-10-13 16:52:34'),(15,'Jáuregui','2026-10-13 16:52:34','2026-10-13 16:52:34'),(16,'Junin · Rafael Urdaneta','2026-10-13 16:52:34','2026-10-13 16:52:34'),(17,'Libertador','2026-10-13 16:52:34','2026-10-13 16:52:34'),(18,'Michelena','2026-10-13 16:52:34','2026-10-13 16:52:34'),(19,'Panamericano · San Judas Tadeo','2026-10-13 16:52:34','2026-10-13 16:52:34'),(20,'Sabaneta','2026-10-13 16:52:34','2026-10-13 16:52:34'),(21,'Samuel Darío Maldonado','2026-10-13 16:52:34','2026-10-13 16:52:34'),(22,'San Josecito','2026-10-13 16:52:34','2026-10-13 16:52:34'),(23,'Sucre','2026-10-13 16:52:34','2026-10-13 16:52:34'),(24,'Ureña','2026-10-13 16:52:34','2026-10-13 16:52:34'),(25,'Uribante','2026-10-13 16:52:34','2026-10-13 16:52:34');
/*!40000 ALTER TABLE `asic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comite`
--

DROP TABLE IF EXISTS `comite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comite` (
  `id_comite` int(11) NOT NULL AUTO_INCREMENT,
  `id_asic` int(11) NOT NULL,
  `id_usuario_registro` int(11) NOT NULL,
  `estado` varchar(100) DEFAULT NULL,
  `municipio` varchar(100) DEFAULT NULL,
  `parroquia` varchar(100) DEFAULT NULL,
  `centro_dispensador` varchar(100) DEFAULT NULL,
  `nombre_centro` varchar(200) DEFAULT NULL,
  `nombre_comite` varchar(200) DEFAULT NULL,
  `eliminado` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_comite`),
  KEY `id_asic` (`id_asic`),
  KEY `id_usuario_registro` (`id_usuario_registro`),
  CONSTRAINT `comite_ibfk_1` FOREIGN KEY (`id_asic`) REFERENCES `asic` (`id_asic`),
  CONSTRAINT `comite_ibfk_2` FOREIGN KEY (`id_usuario_registro`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comite`
--

LOCK TABLES `comite` WRITE;
/*!40000 ALTER TABLE `comite` DISABLE KEYS */;
/*!40000 ALTER TABLE `comite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `municipio`
--

DROP TABLE IF EXISTS `municipio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `municipio` (
  `id_municipio` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_municipio`),
  UNIQUE KEY `ux_municipio_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `municipio`
--

LOCK TABLES `municipio` WRITE;
/*!40000 ALTER TABLE `municipio` DISABLE KEYS */;
INSERT INTO `municipio` VALUES (1,'Andrés Bello','2026-10-13 18:05:38','2026-10-13 18:05:38'),(2,'Antonio Rómulo Costa','2026-10-13 18:05:38','2026-10-13 18:05:38'),(3,'Ayacucho','2026-10-13 18:05:38','2026-10-13 18:05:38'),(4,'Bolívar','2026-10-13 18:05:38','2026-10-13 18:05:38'),(5,'Cárdenas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(6,'Córdoba','2026-10-13 18:05:38','2026-10-13 18:05:38'),(7,'Fernández Feo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(8,'Francisco de Miranda','2026-10-13 18:05:38','2026-10-13 18:05:38'),(9,'García de Hevia','2026-10-13 18:05:38','2026-10-13 18:05:38'),(10,'Guásimos','2026-10-13 18:05:38','2026-10-13 18:05:38'),(11,'Independencia','2026-10-13 18:05:38','2026-10-13 18:05:38'),(12,'Jáuregui','2026-10-13 18:05:38','2026-10-13 18:05:38'),(13,'José María Vargas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(14,'Junín','2026-10-13 18:05:38','2026-10-13 18:05:38'),(15,'Libertad','2026-10-13 18:05:38','2026-10-13 18:05:38'),(16,'Libertador','2026-10-13 18:05:38','2026-10-13 18:05:38'),(17,'Lobatera','2026-10-13 18:05:38','2026-10-13 18:05:38'),(18,'Michelena','2026-10-13 18:05:38','2026-10-13 18:05:38'),(19,'Panamericano','2026-10-13 18:05:38','2026-10-13 18:05:38'),(20,'Pedro María Ureña','2026-10-13 18:05:38','2026-10-13 18:05:38'),(21,'Rafael Urdaneta','2026-10-13 18:05:38','2026-10-13 18:05:38'),(22,'Samuel Darío Maldonado','2026-10-13 18:05:38','2026-10-13 18:05:38'),(23,'San Cristóbal','2026-10-13 18:05:38','2026-10-13 18:05:38'),(24,'San Judas Tadeo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(25,'Seboruco','2026-10-13 18:05:38','2026-10-13 18:05:38'),(26,'Simón Rodríguez','2026-10-13 18:05:38','2026-10-13 18:05:38'),(27,'Sucre','2026-10-13 18:05:38','2026-10-13 18:05:38'),(28,'Torbes','2026-10-13 18:05:38','2026-10-13 18:05:38'),(29,'Uribante','2026-10-13 18:05:38','2026-10-13 18:05:38');
/*!40000 ALTER TABLE `municipio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parroquia`
--

DROP TABLE IF EXISTS `parroquia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parroquia` (
  `id_parroquia` int(11) NOT NULL AUTO_INCREMENT,
  `id_municipio` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_parroquia`),
  UNIQUE KEY `ux_parroquia_municipio_nombre` (`id_municipio`,`nombre`),
  CONSTRAINT `parroquia_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipio` (`id_municipio`)
) ENGINE=InnoDB AUTO_INCREMENT=265 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parroquia`
--

LOCK TABLES `parroquia` WRITE;
/*!40000 ALTER TABLE `parroquia` DISABLE KEYS */;
INSERT INTO `parroquia` VALUES (1,1,'Cordero','2026-10-13 18:05:38','2026-10-13 18:05:38'),(2,2,'Virgen del Carmen','2026-10-13 18:05:38','2026-10-13 18:05:38'),(3,3,'San Juan de Colón','2026-10-13 18:05:38','2026-10-13 18:05:38'),(4,3,'Rivas Berti','2026-10-13 18:05:38','2026-10-13 18:05:38'),(5,3,'San Pedro del Río','2026-10-13 18:05:38','2026-10-13 18:05:38'),(6,4,'San Antonio del Táchira','2026-10-13 18:05:38','2026-10-13 18:05:38'),(7,4,'Palotal','2026-10-13 18:05:38','2026-10-13 18:05:38'),(8,4,'Juan Vicente Gómez','2026-10-13 18:05:38','2026-10-13 18:05:38'),(9,4,'Isaías Medina Angarita','2026-10-13 18:05:38','2026-10-13 18:05:38'),(10,5,'Táriba','2026-10-13 18:05:38','2026-10-13 18:05:38'),(11,5,'Amenodoro Rangel Lamús','2026-10-13 18:05:38','2026-10-13 18:05:38'),(12,5,'La Florida','2026-10-13 18:05:38','2026-10-13 18:05:38'),(13,6,'Santa Ana del Táchira','2026-10-13 18:05:38','2026-10-13 18:05:38'),(14,7,'San Rafael del Piñal','2026-10-13 18:05:38','2026-10-13 18:05:38'),(15,7,'Alberto Adriani','2026-10-13 18:05:38','2026-10-13 18:05:38'),(16,7,'Santo Domingo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(17,8,'San José de Bolívar','2026-10-13 18:05:38','2026-10-13 18:05:38'),(18,9,'La Fría','2026-10-13 18:05:38','2026-10-13 18:05:38'),(19,9,'Boca de Grita','2026-10-13 18:05:38','2026-10-13 18:05:38'),(20,9,'José Antonio Páez','2026-10-13 18:05:38','2026-10-13 18:05:38'),(21,10,'Palmira','2026-10-13 18:05:38','2026-10-13 18:05:38'),(22,11,'Capacho Nuevo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(23,11,'Juan Germán Roscio','2026-10-13 18:05:38','2026-10-13 18:05:38'),(24,11,'Román Cárdenas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(25,12,'La Grita','2026-10-13 18:05:38','2026-10-13 18:05:38'),(26,12,'Emilio Constantino Guerrero','2026-10-13 18:05:38','2026-10-13 18:05:38'),(27,12,'Monseñor Miguel Antonio Salas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(28,13,'El Cobre','2026-10-13 18:05:38','2026-10-13 18:05:38'),(29,14,'Rubio','2026-10-13 18:05:38','2026-10-13 18:05:38'),(30,14,'Bramón','2026-10-13 18:05:38','2026-10-13 18:05:38'),(31,14,'La Petrólea','2026-10-13 18:05:38','2026-10-13 18:05:38'),(32,14,'Quinimarí','2026-10-13 18:05:38','2026-10-13 18:05:38'),(33,15,'Capacho Viejo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(34,15,'Cipriano Castro','2026-10-13 18:05:38','2026-10-13 18:05:38'),(35,15,'Manuel Felipe Rugeles','2026-10-13 18:05:38','2026-10-13 18:05:38'),(36,16,'Abejales','2026-10-13 18:05:38','2026-10-13 18:05:38'),(37,16,'Doradas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(38,16,'Emeterio Ochoa','2026-10-13 18:05:38','2026-10-13 18:05:38'),(39,16,'San Joaquín de Navay','2026-10-13 18:05:38','2026-10-13 18:05:38'),(40,17,'Lobatera','2026-10-13 18:05:38','2026-10-13 18:05:38'),(41,17,'Constitución','2026-10-13 18:05:38','2026-10-13 18:05:38'),(42,18,'Michelena','2026-10-13 18:05:38','2026-10-13 18:05:38'),(43,19,'San Pablo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(44,19,'La Palmita','2026-10-13 18:05:38','2026-10-13 18:05:38'),(45,20,'Ureña','2026-10-13 18:05:38','2026-10-13 18:05:38'),(46,20,'Nueva Arcadia','2026-10-13 18:05:38','2026-10-13 18:05:38'),(47,21,'Delicias','2026-10-13 18:05:38','2026-10-13 18:05:38'),(48,22,'La Tendida','2026-10-13 18:05:38','2026-10-13 18:05:38'),(49,22,'Boconó','2026-10-13 18:05:38','2026-10-13 18:05:38'),(50,22,'Hernández','2026-10-13 18:05:38','2026-10-13 18:05:38'),(51,23,'La Concordia','2026-10-13 18:05:38','2026-10-13 18:05:38'),(52,23,'Pedro María Morantes','2026-10-13 18:05:38','2026-10-13 18:05:38'),(53,23,'San Juan Bautista','2026-10-13 18:05:38','2026-10-13 18:05:38'),(54,23,'San Sebastián','2026-10-13 18:05:38','2026-10-13 18:05:38'),(55,23,'Francisco Romero Lobo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(56,24,'San Judas Tadeo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(57,25,'Seboruco','2026-10-13 18:05:38','2026-10-13 18:05:38'),(58,26,'San Simón','2026-10-13 18:05:38','2026-10-13 18:05:38'),(59,27,'Sucre','2026-10-13 18:05:38','2026-10-13 18:05:38'),(60,27,'Eleazar López Contreras','2026-10-13 18:05:38','2026-10-13 18:05:38'),(61,27,'San Pablo','2026-10-13 18:05:38','2026-10-13 18:05:38'),(62,28,'San Josecito','2026-10-13 18:05:38','2026-10-13 18:05:38'),(63,29,'Pregonero','2026-10-13 18:05:38','2026-10-13 18:05:38'),(64,29,'Cárdenas','2026-10-13 18:05:38','2026-10-13 18:05:38'),(65,29,'Juan Pablo Peñaloza','2026-10-13 18:05:38','2026-10-13 18:05:38'),(66,29,'Potosí','2026-10-13 18:05:38','2026-10-13 18:05:38');
/*!40000 ALTER TABLE `parroquia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_actividad`
--

DROP TABLE IF EXISTS `tipo_actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_actividad` (
  `id_tipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_tipo`),
  UNIQUE KEY `ux_tipo_actividad_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_actividad`
--

LOCK TABLES `tipo_actividad` WRITE;
/*!40000 ALTER TABLE `tipo_actividad` DISABLE KEYS */;
INSERT INTO `tipo_actividad` VALUES (1,'Salud toca tu puerta','2026-10-13 16:52:34','2026-10-13 16:52:34'),(2,'Sesiones educativas','2026-10-13 16:52:34','2026-10-13 16:52:34'),(3,'Los Comités de Salud van a la escuela','2026-10-13 16:52:34','2026-10-13 16:52:34'),(4,'Actividades de Promoción y Prevención Social','2026-10-13 16:52:34','2026-10-13 16:52:34'),(5,'Participación Activa en Jornadas','2026-10-13 16:52:34','2026-10-13 16:52:34'),(6,'Participación Activa en Inmunizaciones','2026-10-13 16:52:34','2026-10-13 16:52:34'),(7,'Entrevista servicio social','2026-10-13 16:52:34','2026-10-13 16:52:34');
/*!40000 ALTER TABLE `tipo_actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_voceria`
--

DROP TABLE IF EXISTS `tipo_voceria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_voceria` (
  `id_tipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_tipo`),
  UNIQUE KEY `ux_tipo_voceria_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_voceria`
--

LOCK TABLES `tipo_voceria` WRITE;
/*!40000 ALTER TABLE `tipo_voceria` DISABLE KEYS */;
INSERT INTO `tipo_voceria` VALUES (1,'V. CONTRALORÍA','2026-10-13 16:52:34','2026-10-13 16:52:34'),(2,'V. DEL ADULTO MAYOR','2026-10-13 16:52:34','2026-10-13 16:52:34'),(3,'V. DE ENFERMEDADES CRÓNICAS TRASMISIBLES Y NO TRASMISIBLES','2026-10-13 16:52:34','2026-10-13 16:52:34'),(4,'V. DE PERSONAS CON DISCAPACIDAD, ENCAMADOS Y CUIDADORES EN SALUD','2026-10-13 16:52:34','2026-10-13 16:52:34'),(5,'V. DE SALUD Y VIDA','2026-10-13 16:52:34','2026-10-13 16:52:34'),(6,'V. DE NIÑOS, NIÑAS Y ADOLESCENTES','2026-10-13 16:52:34','2026-10-13 16:52:34'),(7,'V. DE LA JUVENTUD EN SALUD','2026-10-13 16:52:34','2026-10-13 16:52:34'),(8,'V. DE EDUCACIÓN POPULAR EN SALUD INTERCULTURAL Y ANCESTRAL','2026-10-13 16:52:34','2026-10-13 16:52:34'),(9,'V. DE INMUNIZACIONES','2026-10-13 16:52:34','2026-10-13 16:52:34'),(10,'V. DE PROYECTOS EN SALUD','2026-10-13 16:52:34','2026-10-13 16:52:34');
/*!40000 ALTER TABLE `tipo_voceria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nombre_completo` varchar(120) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `apellido` varchar(100) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'lector',
  `email_verificado` tinyint(1) NOT NULL DEFAULT 0,
  `codigo_verificacion` varchar(20) DEFAULT NULL,
  `codigo_verificacion_expira` datetime DEFAULT NULL,
  `codigo_recuperacion` varchar(20) DEFAULT NULL,
  `codigo_recuperacion_expira` datetime DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (2,'admin','$2b$12$zjzbxu6Wm3Qb0H2TZY5aFOd3runZ7hRfKh8tDwdOaRZ0sZcZg6hMm','Usuario propietario',NULL,NULL,'keivymora1@gmail.com','propietario',1,NULL,NULL,NULL,NULL,1,'2026-10-13 17:48:42','2026-10-13 17:48:42');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voceria`
--

DROP TABLE IF EXISTS `voceria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voceria` (
  `id_voceria` int(11) NOT NULL AUTO_INCREMENT,
  `id_comite` int(11) NOT NULL,
  `id_tipo_voceria` int(11) NOT NULL,
  `nombres` varchar(150) NOT NULL,
  `ci` varchar(30) NOT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `edad` int(11) DEFAULT NULL,
  `sexo` enum('M','F') DEFAULT NULL,
  `profesion` varchar(120) DEFAULT NULL,
  `correo` varchar(120) DEFAULT NULL,
  `fechas_eleccion` date DEFAULT NULL,
  `eliminado` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_voceria`),
  KEY `id_comite` (`id_comite`),
  KEY `id_tipo_voceria` (`id_tipo_voceria`),
  CONSTRAINT `voceria_ibfk_1` FOREIGN KEY (`id_comite`) REFERENCES `comite` (`id_comite`),
  CONSTRAINT `voceria_ibfk_2` FOREIGN KEY (`id_tipo_voceria`) REFERENCES `tipo_voceria` (`id_tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voceria`
--

LOCK TABLES `voceria` WRITE;
/*!40000 ALTER TABLE `voceria` DISABLE KEYS */;
/*!40000 ALTER TABLE `voceria` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-14 11:34:06
