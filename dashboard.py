#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:  /home/al/system_files/projects/py/dashboard.py
#
# Copyright 2026 AL Haines

import sys
import shlex
import subprocess
sys.path.insert(0, '/home/al/system_files/projects')
sys.path.insert(0, '/home/al/system_files/projects/py')

try:
    from MySql import MySQL
    from check_imports import ensure_module
    from runner import stream_command
    from dep_checker import DepChecker
except ImportError as e:
    print(f"ERROR: Critical modules not found: {e}", file=sys.stderr)
    sys.exit(1)

if not ensure_module('textual'):
    sys.exit("Error: 'textual' library is required but could not be installed. Exiting.")

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Log, Input
from textual.message import Message

def get_dashboard_commands():
    db_manager = MySQL()
    query = "SELECT `key`, `name`, `command_type`, `command_string`, `requires_input`, `quote_input`, `big_display` FROM `dashboard_commands` WHERE `enabled` = 1 ORDER BY `sort_order`, `id`"
    try:
        commands = db_manager.get_data(query)
        return commands
    except Exception as e:
        print(f"A database error occurred: {e}", file=sys.stderr)
        return None

class CommandFinished(Message):
    """Posted when a command worker has finished executing."""
    pass

class DashboardApp(App):
    CSS_PATH = "dashboard.css"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.check_system_dependencies()

        raw_commands = get_dashboard_commands()
        if raw_commands is None:
            sys.exit("CRITICAL: Failed to load commands from database.")
        self.command_map = {cmd['key']: cmd for cmd in raw_commands}
        self.active_command = None

    def check_system_dependencies(self):
        """Validates critical modules using DepChecker."""
        checker = DepChecker()
        checker('pymysql')
        checker('textual')

    def compose(self) -> ComposeResult:
        yield Header(name="Haines Homelab Dashboard")
        yield Footer()
        with Container(id="app-grid"):
            with Container(id="sidebar-container"):
                yield Static("MENU", id="sidebar-title")
                if self.command_map:
                    for key, command_data in self.command_map.items():
                        menu_line = f" ({key}) {command_data.get('name')}"
                        yield Static(menu_line)
                else:
                    yield Static("No commands found in database.")
            with Vertical(id="main-container"):
                yield Log(id="output-log", highlight=True)
                yield Input(placeholder="Enter your input here...", id="command-input", classes="hidden")

    def on_mount(self) -> None:
        log = self.query_one(Log)
        log.write_line("Welcome to your Homelab Dashboard.")
        log.write_line("Press a key from the menu to run a command.")
        self.query_one("#sidebar-container").focus()

    def on_command_finished(self, message: CommandFinished) -> None:
        self.query_one("#sidebar-container").focus()

    def on_key(self, event) -> None:
        if event.key in self.command_map:
            command_data = self.command_map[event.key]

            if command_data.get('requires_input'):
                self.active_command = command_data
                inp = self.query_one("#command-input")
                log = self.query_one(Log)
                log.clear()
                log.write_line(f"Input required for '{command_data['name']}'.")
                inp.placeholder = f"Enter text for '{command_data['name']}' and press Enter"
                inp.remove_class("hidden")
                inp.focus()
            else:
                self.dispatch_command(command_data)

    def dispatch_command(self, command_data: dict, user_input: str = "") -> None:
        final_command = command_data['command_string']
        if user_input:
            if command_data.get('quote_input'):
                final_command += " " + shlex.quote(user_input)
            else:
                final_command += " " + user_input

        # Robustly parse big_display flag: 1 = fullscreen, 0 = log window
        raw_big = command_data.get('big_display', 1)
        try:
            is_big = int(raw_big) if raw_big is not None else 1
        except (ValueError, TypeError):
            is_big = 1

        if is_big == 1:
            self.run_fullscreen_app(final_command)
        else:
            self.run_command_in_log(final_command, command_data)

    def run_fullscreen_app(self, command_string: str) -> None:
        with self.suspend():
            try:
                subprocess.run(f"clear && {command_string}", shell=True)
                input("\nPress Enter to return to the dashboard...")
            except Exception as e:
                print(f"Error running command '{command_string}': {e}")
                input("Press Enter to continue...")

    def run_command_in_log(self, final_command: str, command_data: dict) -> None:
        log = self.query_one(Log)
        log.clear()
        log.write_line(f"Running '{command_data['name']}'...")
        self.query_one("#command-input").add_class("hidden")
        self.run_worker(self.execute_command_and_update_log(final_command, command_data['command_type']), exclusive=True)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.value
        if self.active_command and user_input:
            cmd = self.active_command
            self.active_command = None
            event.input.value = ""
            self.dispatch_command(cmd, user_input)

    async def execute_command_and_update_log(self, command_string: str, command_type: str) -> None:
        log = self.query_one("#output-log")
        log.clear()
        try:
            for line in stream_command(command_string, command_type):
                log.write_line(line)
        except Exception as e:
            log.write_line(f"An error occurred in the dashboard worker: {e}")
        finally:
            self.post_message(CommandFinished())

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
#============= end of code      ================#
