# Haines Homelab Dashboard v1.0

A simple, fast, and efficient Text-based User Interface (TUI) for running common homelab scripts and commands. The dashboard is built with the Python Textual framework and is designed to be driven entirely by the keyboard.
Provided for your use are some sample apps to make your bash experience enjoyable! put them in your path and edit dashboard_commands.sql with your paths

## Features

-   **Database-Driven Menu:** The menu is dynamically generated from a MySQL database table, making it easy to add, remove, or modify commands without changing the application code.
-   **Streaming Output:** Long-running commands (like system updates) stream their output to the screen in real-time, preventing the UI from hanging.
-   **Interactive Command Support:** Supports commands that require user input, as well as commands that need root privileges (via a graphical `sudo` password prompt).
-   **Full-Screen Application Support:** Can launch full-screen terminal applications like `far2l` by suspending the dashboard and resuming when the application exits.

## Requirements

1.  A Linux system with Python 3.
2.  A working MySQL/MariaDB server.
3.  The `als` database must exist.
4.  The `als.dashboard_commands` table must be created in the database.

## Installation

1.  Place the entire project folder on your system (e.g., in `~/projects/dashboard_v1.0`).
2.  Ensure the `MySql.py` module is present in the directory.
3.  Make the installation script executable: `chmod +x install.sh`
4.  Run the installation script: `./install.sh`

The script will check for necessary system tools (`python3`, `pip`) and install the required Python libraries listed in `requirements.txt`.

## Database Setup

Before running the dashboard for the first time, you must create the `dashboard_commands` table in your `als` database. You can use the following SQL command:

```sql
CREATE TABLE `dashboard_commands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` char(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `command_type` enum('shell','python','internal') NOT NULL,
  `command_string` text NOT NULL,
  `requires_input` tinyint(1) NOT NULL DEFAULT '0',
  `quote_input` tinyint(1) NOT NULL DEFAULT '0',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

You can then populate this table with the commands you wish to appear in the menu.

## Usage

After installation, simply run the main application file:
```bash
python3 /path/to/project/dashboard.py
```
