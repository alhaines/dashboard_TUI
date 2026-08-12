
DROP TABLE IF EXISTS `dashboard_commands`;
CREATE TABLE IF NOT EXISTS `dashboard_commands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sort_order` int NOT NULL DEFAULT '0',
  `key` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `command_type` enum('shell','python','internal') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `command_string` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `requires_input` tinyint(1) NOT NULL DEFAULT '0',
  `quote_input` tinyint(1) NOT NULL DEFAULT '0',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `big_display` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `dashboard_commands` (`id`, `sort_order`, `key`, `name`, `command_type`, `command_string`, `requires_input`, `quote_input`, `enabled`, `big_display`) VALUES
(1, 1, 'a', 'Ask AI (ai01.py)', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/ai.py ask', 1, 0, 1, 1),
(2, 2, 'd', 'Directory Listing +', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/rich_dfb.py', 0, 0, 1, 1),
(3, 3, 'f', 'File Manager', 'shell', 'far2l --tty', 0, 0, 1, 1),
(4, 4, 'u', 'Update System', 'shell', 'clear; echo \'Upgrading....!\'; sudo apt upgrade -y', 0, 0, 1, 1),
(5, 5, 's', 'Search AI (ai01.py)', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/ai.py search ', 1, 1, 1, 1),
(6, 6, 'b', 'Backup new Files', 'shell', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/backup_functions.py ', 0, 0, 1, 1),
(7, 7, '0', 'Add Journal Entry', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/journal.py update ', 1, 1, 1, 1),
(8, 8, '1', 'Journal Preview', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/showme.py als last journal', 0, 0, 1, 1),
(9, 9, '2', 'Journal Dump', 'python', '/home/al/miniconda3/envs/py/bin/python3 /home/al/system_files/projects/py/showme.py als display journal', 0, 0, 1, 1);
