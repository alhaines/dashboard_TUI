# Haines Homelab Dashboard (DashboardTUI)

A simple, fast, and efficient Text-based User Interface (TUI) for running common homelab scripts and commands via ssh or shell. The dashboard is built with the Python Textual framework and is designed to be driven entirely by the keyboard.

A modular, dynamic Textual User Interface (TUI) designed for Linux homelabs, driven entirely by a MySQL database backend.

## What is a TUI?
A Text User Interface (TUI) is a program interface that builds interactive graphical-like layouts (menus, boxes, text inputs, logs) entirely within a standard terminal or text console using character graphics.

## How It Works (Dynamic MySQL Architecture)
Unlike static menu scripts, this Dashboard is completely dynamic. All sidebar menu items, command strings, execution types, input requirements, and display modes (using the `big_display` flag to toggle between full-screen terminal apps and inline log streaming) are queried live from a MySQL database table (`dashboard_commands`).

## Features
Database-Driven Menu: The menu is dynamically generated from a MySQL database table, making it easy to add, remove, or modify commands without changing the application code.
Streaming Output: Long-running commands (like system updates) stream their output to the screen in real-time, preventing the UI from hanging.
Interactive Command Support: Supports commands that require user input, as well as commands that need root privileges (via a graphical sudo password prompt).
Full-Screen Application Support: Can launch full-screen terminal applications like far2l by suspending the dashboard and resuming when the application exits.

## Requirements
A Linux system with Python 3.
A working MySQL/MariaDB server.
The main database must exist.
The main.dashboard_commands table must be created in the database.

## Manual Documentation Installation (Optional)
This project includes a man page for easy reference. To install it manually:

# Ensure the target directory exists:
sudo mkdir -p /usr/local/share/man/man1
# Copy the man page file to the system directory:
sudo cp /path/to/your/dashboard_TUI/dashboard.1 /usr/local/share/man/man1/
# Compress the man page (optional but good practice):
sudo gzip /usr/local/share/man/man1/dashboard.1
# Update the man database:
sudo mandb
# After installation, you can view the documentation at any time by running man dashboard.

## Requirements

1.  A Linux system with Python 3.
2.  A working MySQL/MariaDB server.
3.  The `main` database must exist.
4.  The `main.dashboard_commands` table must be created in the database.

## Installation & Setup

### 1. Copy Files
Copy the required files into your Python project directory (e.g., `/home/$USER/system_files/projects/dashboard_TUI/`):
* `dashboard.py`
* `dashboard.css`
* `dashboard.sql`
* `MySql.py`
* `check_imports.py`
* `runner.py`
* `dep_checker.py`

### 2. Set Permissions
Grant executable permissions to the main dashboard script:
```bash
chmod +x /home/$USER/system_files/projects/py/dashboard.py

### 3. setup commands table
Before running the dashboard for the first time, you must create the dashboard_commands table. An example SQL file, dashboard_commands.sql, is included in this project to help you get started. You can import this file using a tool like phpMyAdmin or run it from the command line:

mysql -u $USER -p your_database < dashboard_commands.sql

check out the companion app to edit the commands table:

