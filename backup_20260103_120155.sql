-- MySQL dump 10.13  Distrib 9.5.0, for macos15 (arm64)
--
-- Host: localhost    Database: smart_classroom_scheduler
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
-- Table structure for table `batches`
--

DROP TABLE IF EXISTS `batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `branch` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `section` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `semester` int NOT NULL,
  `academic_year` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_count` int DEFAULT NULL,
  `shift` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority_for_allocation` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batches`
--

LOCK TABLES `batches` WRITE;
/*!40000 ALTER TABLE `batches` DISABLE KEYS */;
/*!40000 ALTER TABLE `batches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classroom_allocations`
--

DROP TABLE IF EXISTS `classroom_allocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classroom_allocations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `batch_id` int NOT NULL,
  `day_of_week` int NOT NULL,
  `time_slot` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority_score` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `classroom_allocations_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`),
  CONSTRAINT `classroom_allocations_ibfk_2` FOREIGN KEY (`batch_id`) REFERENCES `batches` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classroom_allocations`
--

LOCK TABLES `classroom_allocations` WRITE;
/*!40000 ALTER TABLE `classroom_allocations` DISABLE KEYS */;
/*!40000 ALTER TABLE `classroom_allocations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classrooms`
--

DROP TABLE IF EXISTS `classrooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classrooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `capacity` int NOT NULL,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment` text COLLATE utf8mb4_unicode_ci,
  `is_fixed_allocation` tinyint(1) DEFAULT NULL,
  `fixed_batch_id` int DEFAULT NULL,
  `priority_level` int DEFAULT NULL,
  `can_be_shared` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fixed_batch_id` (`fixed_batch_id`),
  CONSTRAINT `classrooms_ibfk_1` FOREIGN KEY (`fixed_batch_id`) REFERENCES `batches` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classrooms`
--

LOCK TABLES `classrooms` WRITE;
/*!40000 ALTER TABLE `classrooms` DISABLE KEYS */;
/*!40000 ALTER TABLE `classrooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `specialization` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_hours_per_day` int DEFAULT NULL,
  `max_hours_per_week` int DEFAULT NULL,
  `avg_leaves_per_month` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty_subjects`
--

DROP TABLE IF EXISTS `faculty_subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty_subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faculty_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branch` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `semester` int DEFAULT NULL,
  `is_primary` tinyint(1) DEFAULT NULL,
  `priority` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `faculty_subjects_ibfk_1` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`id`),
  CONSTRAINT `faculty_subjects_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty_subjects`
--

LOCK TABLES `faculty_subjects` WRITE;
/*!40000 ALTER TABLE `faculty_subjects` DISABLE KEYS */;
/*!40000 ALTER TABLE `faculty_subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credits` int DEFAULT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `semester` int DEFAULT NULL,
  `hours_per_week` int DEFAULT NULL,
  `requires_lab` tinyint(1) DEFAULT NULL,
  `scheduling_preference` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `continuous_block_size` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetable_entries`
--

DROP TABLE IF EXISTS `timetable_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable_entries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timetable_id` int NOT NULL,
  `batch_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `faculty_id` int NOT NULL,
  `classroom_id` int NOT NULL,
  `day_of_week` int NOT NULL,
  `time_slot` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_temporary_allocation` tinyint(1) DEFAULT NULL,
  `original_classroom_owner_id` int DEFAULT NULL,
  `allocation_reason` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `timetable_id` (`timetable_id`),
  KEY `batch_id` (`batch_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `original_classroom_owner_id` (`original_classroom_owner_id`),
  CONSTRAINT `timetable_entries_ibfk_1` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`),
  CONSTRAINT `timetable_entries_ibfk_2` FOREIGN KEY (`batch_id`) REFERENCES `batches` (`id`),
  CONSTRAINT `timetable_entries_ibfk_3` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `timetable_entries_ibfk_4` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`id`),
  CONSTRAINT `timetable_entries_ibfk_5` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`),
  CONSTRAINT `timetable_entries_ibfk_6` FOREIGN KEY (`original_classroom_owner_id`) REFERENCES `batches` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetable_entries`
--

LOCK TABLES `timetable_entries` WRITE;
/*!40000 ALTER TABLE `timetable_entries` DISABLE KEYS */;
/*!40000 ALTER TABLE `timetable_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetables`
--

DROP TABLE IF EXISTS `timetables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetables` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch_id` int NOT NULL,
  `academic_year` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `semester` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timing_config` text COLLATE utf8mb4_unicode_ci,
  `college_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `timetables_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batches` (`id`),
  CONSTRAINT `timetables_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetables`
--

LOCK TABLES `timetables` WRITE;
/*!40000 ALTER TABLE `timetables` DISABLE KEYS */;
/*!40000 ALTER TABLE `timetables` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@local.dev','scrypt:32768:8:1$YT1xxyXlk6qehGNN$be66e2a1d376a94c1a605a1f9d96891db4b6748bd712d5e9f24f51000a2d3fea9f86da8f792ab9d845941753a67882e335fb1b18c85a74dd9c5e166e378ba733','admin',1,'2026-01-03 06:28:28'),(2,'gottipallisravan@gmail.com','gottipallisravan@gmail.com','scrypt:32768:8:1$LLCIU07ElobyI632$e233271edde0e12a206d618429d3637cd5b05ce0bd13ae6edea8ea88406c09816295dd571c11de1bde2e491941f8b30df4ff542db2c6f215dfbafd8cbbaa9f71','user',1,'2026-01-03 06:29:31');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
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

-- Dump completed on 2026-01-03 12:02:00
