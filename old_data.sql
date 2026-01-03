-- MySQL dump 10.13  Distrib 9.5.0, for macos15 (arm64)
--
-- Host: localhost    Database: timetable_db
-- ------------------------------------------------------
-- Server version	9.5.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '615402e4-b0c5-11f0-bd02-c745023a1ee7:1-765';

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) NOT NULL,
  `hours_per_week` int DEFAULT '3',
  `is_practical` tinyint(1) DEFAULT '0',
  `credits` int DEFAULT '3',
  `lecture_hours` int DEFAULT '0',
  `tutorial_hours` int DEFAULT '0',
  `lab_hours` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES (1,'Optimization Techniques','OT',2,0,2,2,0,0),(2,'Probability & Statistics','PS',3,0,3,3,0,0),(3,'Machine Learning','ML',3,0,3,3,0,0),(4,'Advanced Data Structures & Also. Analysis','ADSAA',3,0,3,3,0,0),(5,'Digital Logic & Computer Org.','DLCO',3,0,3,3,0,0),(6,'AIML LAB','AIML LAB',3,1,2,0,0,3),(7,'ADSAA LAB','ADSAA LAB',3,1,2,0,0,3),(8,'Full Stack Development-I','FSD-I LAB',3,1,2,0,1,2),(9,'Design Thinking & Innovation','DTI',3,0,2,1,0,2),(10,'Environmental Science','ES',2,0,0,2,0,0),(11,'Humanities & Management','H&M',3,0,3,3,0,0);
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (1,'Dr. K Suresh Babu','k.sureshbabu@example.com','CSE'),(2,'Dr. N U B Varma','nub.varma@example.com','CSE'),(3,'Smt. D Hema Latha','d.hemalatha@example.com','CSE'),(4,'Dr. P Bharat Siva Varma','pbs.varma@example.com','CSE'),(5,'Smt. P Neelima','p.neelima@example.com','CSE'),(6,'Smt. A L Lavanya','al.lavanya@example.com','CSE'),(7,'Smt. P Saroja','p.saroja@example.com','CSE'),(8,'Smt. K Raja Rajeswari','k.rajarajeswari@example.com','CSE'),(9,'Smt. V Anjani Kranti','v.anjani@example.com','CSE'),(10,'Sri J Jeevan Kumar','j.jeevan@example.com','CSE');
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classrooms`
--

DROP TABLE IF EXISTS `classrooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classrooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `capacity` int NOT NULL,
  `has_projector` tinyint(1) DEFAULT '0',
  `is_lab` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classrooms`
--

LOCK TABLES `classrooms` WRITE;
/*!40000 ALTER TABLE `classrooms` DISABLE KEYS */;
INSERT INTO `classrooms` VALUES (1,'C-402',60,1,0),(2,'C-109',30,1,1),(3,'B-201',30,1,1),(4,'B-301',30,1,1);
/*!40000 ALTER TABLE `classrooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `batches`
--

DROP TABLE IF EXISTS `batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `size` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batches`
--

LOCK TABLES `batches` WRITE;
/*!40000 ALTER TABLE `batches` DISABLE KEYS */;
INSERT INTO `batches` VALUES (1,'Sec-A II B.Tech AIML',60);
/*!40000 ALTER TABLE `batches` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-03 12:04:34
