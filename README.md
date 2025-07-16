# Haines Homelab Dashboard v1.0

A simple, fast, and efficient Text-based User Interface (TUI) for running common homelab scripts and commands. The dashboard is built with the Python Textual framework and is designed to be driven entirely by the keyboard.

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

1.  Download and extract the project ZIP file to a location of your choice (e.g., `~/Downloads/dashboard_TUI`).
2.  Navigate into the project directory in your terminal:
    `cd /path/to/dashboard_TUI`
3.  Make the installation script executable:
    `chmod +x install.sh`
4.  Run the installation script from within the project directory:
    `./install.sh`

The script will guide you through installing dependencies.

## Manual Documentation Installation (Optional)

This project includes a `man` page for easy reference. To install it manually:

1.  Ensure the target directory exists:
    `sudo mkdir -p /usr/local/share/man/man1`
2.  Copy the `man` page file to the system directory:
    `sudo cp /path/to/your/dashboard_TUI/dashboard.1 /usr/local/share/man/man1/`
3.  Compress the `man` page (optional but good practice):
    `sudo gzip /usr/local/share/man/man1/dashboard.1`
4.  Update the `man` database:
    `sudo mandb`

After installation, you can view the documentation at any time by running `man dashboard`.

## Database Setup

... (Rest of the file remains the same) ...
## Database Setup

Before running the dashboard for the first time, you must create the `dashboard_commands` table. An example SQL file, `dashboard_commands.sql`, is included in this project to help you get started. You can import this file using a tool like phpMyAdmin or run it from the command line:

`mysql -u your_user -p your_database < dashboard_commands.sql`

## Usage

After installation, simply run the main application file:
```bash
python3 /path/to/project/dashboard.py
```
