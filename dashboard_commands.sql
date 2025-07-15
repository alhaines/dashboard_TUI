-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 15, 2025 at 11:46 AM
-- Server version: 8.0.42-0ubuntu0.22.04.2
-- PHP Version: 8.1.2-1ubuntu2.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `als`
--

-- --------------------------------------------------------

--
-- Table structure for table `dashboard_commands`
--

CREATE TABLE `dashboard_commands` (
  `id` int NOT NULL,
  `key` char(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `command_type` enum('shell','python','internal') NOT NULL,
  `command_string` text NOT NULL,
  `requires_input` tinyint(1) NOT NULL DEFAULT '0',
  `quote_input` tinyint(1) NOT NULL DEFAULT '0',
  `enabled` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `dashboard_commands`
--

INSERT INTO `dashboard_commands` (`id`, `key`, `name`, `command_type`, `command_string`, `requires_input`, `quote_input`, `enabled`) VALUES
(1, 'a', 'Ask AI (ai01.py)', 'python', '/home/al/py/ai01.py ask', 1, 0, 1),
(2, 'd', 'Add Journal Entry', 'shell', '/home/al/scripts/ju', 1, 1, 1),
(3, 'm', 'File Manager', 'shell', 'far2l --tty', 0, 0, 1),
(4, 'u', 'Update System', 'shell', 'sudo apt upgrade -y', 0, 0, 1),
(5, 's', 'ShowME', 'shell', '~/py/showme.py', 1, 0, 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dashboard_commands`
--
ALTER TABLE `dashboard_commands`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `key` (`key`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `dashboard_commands`
--
ALTER TABLE `dashboard_commands`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
